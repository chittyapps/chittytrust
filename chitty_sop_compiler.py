"""
ChittySOP - Standard Operating Procedure Compiler and Executor
Part of ChittyCounsel for automated legal workflow execution

Handles:
- YAML SOP compilation to executable plans
- Plan persistence and execution orchestration
- Dependency resolution and validation
- Integration with ChittyID for plan minting
"""

import os
import json
import yaml
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests

@dataclass
class ExecutionRequest:
    """Request to execute a SOP"""
    sop_id: str
    target: Dict[str, Any]
    role: str
    requester: str
    constraints: Dict[str, Any]
    variables: Dict[str, Any]

@dataclass
class ExecutionStep:
    """Individual step in execution plan"""
    step_id: str
    action: str
    tool: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    timeout: int
    required_role: Optional[str]
    validation_rules: List[str]
    retry_policy: Dict[str, Any]

@dataclass
class ExecutionPlan:
    """Compiled execution plan from SOP"""
    plan_id: str
    sop_id: str
    sop_version: str
    target: Dict[str, Any]
    steps: List[ExecutionStep]
    execution_order: List[str]
    execution_groups: List[List[str]]  # For parallel execution
    total_estimated_duration: int
    budget_estimate: Dict[str, float]
    created_at: str
    status: str = 'queued'

@dataclass
class CompilationDiagnostics:
    """Compilation diagnostics and warnings"""
    missing_variables: List[str]
    missing_scopes: List[str]
    missing_tools: List[str]
    role_violations: List[str]
    cycle_errors: List[str]
    budget_warnings: List[str]
    validation_warnings: List[str]

class ChittySOPCompiler:
    """
    Enhanced SOP Compiler for ChittyCounsel
    Compiles YAML SOPs into executable plans with full validation
    """
    
    def __init__(self):
        self.registry_data = self._load_registry_data()
        self.chitty_id_base = os.getenv('CHITTYID_BASE', 'https://chittyid.chitty.cc')
        self.chitty_id_bearer = os.getenv('CHITTYID_BEARER', '')
        
    def _load_registry_data(self) -> Dict[str, Any]:
        """Load tool registry data"""
        # In production, this would load from actual registry
        return {
            'tools': {
                'evidence.add': {
                    'versions': ['1.0.0', '1.1.0'],
                    'endpoint': '/api/evidence/add',
                    'scope_required': ['evidence.write'],
                    'estimated_duration': 30
                },
                'document.notarize': {
                    'versions': ['1.0.0'],
                    'endpoint': '/api/chitty-verify/document',
                    'scope_required': ['document.notarize'],
                    'estimated_duration': 120
                },
                'trust.calculate': {
                    'versions': ['1.0.0'],
                    'endpoint': '/api/trust',
                    'scope_required': ['trust.read'],
                    'estimated_duration': 60
                }
            },
            'roles': {
                'counsel': ['evidence.write', 'document.notarize', 'trust.read'],
                'ops': ['evidence.read', 'trust.read'],
                'admin': ['*']
            }
        }
    
    async def mint_plan_id(self, sop_id: str, version: str) -> str:
        """Mint a ChittyID for the execution plan"""
        try:
            if not self.chitty_id_bearer:
                # Fallback to generated ID if ChittyID service unavailable
                return f"plan_{hashlib.sha256(f'{sop_id}:{version}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:16]}"
            
            response = requests.post(
                f"{self.chitty_id_base}/identity/chitty-id",
                headers={
                    'Authorization': f'Bearer {self.chitty_id_bearer}',
                    'Content-Type': 'application/json'
                },
                json={
                    'kind': 'plan',
                    'hint': {'sop_id': sop_id, 'version': version}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('chitty_id', f'plan_{uuid.uuid4().hex[:16]}')
            else:
                return f'plan_{uuid.uuid4().hex[:16]}'
                
        except Exception as e:
            logging.warning(f"ChittyID minting failed: {e}")
            return f'plan_{uuid.uuid4().hex[:16]}'
    
    async def compile_sop_from_yaml(
        self, 
        yaml_text: str, 
        exec_request: ExecutionRequest,
        plan_id: Optional[str] = None
    ) -> Tuple[Optional[ExecutionPlan], CompilationDiagnostics, bool]:
        """Compile YAML SOP into executable plan"""
        
        diagnostics = CompilationDiagnostics([], [], [], [], [], [], [])
        
        try:
            # Parse YAML
            sop_data = yaml.safe_load(yaml_text)
            
            if not plan_id:
                plan_id = await self.mint_plan_id(
                    exec_request.sop_id, 
                    sop_data.get('version', '1.0.0')
                )
            
            # Validate SOP structure
            if not self._validate_sop_structure(sop_data, diagnostics):
                return None, diagnostics, False
            
            # Compile steps
            steps = []
            for step_data in sop_data.get('steps', []):
                step = self._compile_step(step_data, exec_request, diagnostics)
                if step:
                    steps.append(step)
            
            # Detect dependency cycles
            if self._detect_cycles(steps, diagnostics):
                return None, diagnostics, False
            
            # Calculate execution order
            execution_order = self._calculate_execution_order(steps)
            execution_groups = self._calculate_execution_groups(steps)
            
            # Validate roles and scopes
            self._validate_roles_and_scopes(steps, exec_request, diagnostics)
            
            # Calculate budget estimates
            budget_estimate = self._calculate_budget_estimate(steps, diagnostics)
            total_duration = sum(step.timeout for step in steps)
            
            plan = ExecutionPlan(
                plan_id=plan_id,
                sop_id=exec_request.sop_id,
                sop_version=sop_data.get('version', '1.0.0'),
                target=exec_request.target,
                steps=steps,
                execution_order=execution_order,
                execution_groups=execution_groups,
                total_estimated_duration=total_duration,
                budget_estimate=budget_estimate,
                created_at=datetime.utcnow().isoformat()
            )
            
            # Final validation
            success = len(diagnostics.cycle_errors) == 0 and len(diagnostics.role_violations) == 0
            
            return plan, diagnostics, success
            
        except Exception as e:
            logging.error(f"SOP compilation failed: {e}")
            diagnostics.validation_warnings.append(f"Compilation error: {str(e)}")
            return None, diagnostics, False
    
    def _validate_sop_structure(self, sop_data: Dict[str, Any], diagnostics: CompilationDiagnostics) -> bool:
        """Validate basic SOP structure"""
        required_fields = ['id', 'name', 'version', 'steps']
        
        for field in required_fields:
            if field not in sop_data:
                diagnostics.validation_warnings.append(f"Missing required field: {field}")
                return False
        
        if not isinstance(sop_data['steps'], list) or len(sop_data['steps']) == 0:
            diagnostics.validation_warnings.append("SOP must have at least one step")
            return False
            
        return True
    
    def _compile_step(
        self, 
        step_data: Dict[str, Any], 
        exec_request: ExecutionRequest,
        diagnostics: CompilationDiagnostics
    ) -> Optional[ExecutionStep]:
        """Compile individual step from YAML"""
        
        try:
            step_id = step_data.get('id', f"step_{uuid.uuid4().hex[:8]}")
            tool = step_data.get('tool', '')
            
            # Validate tool exists
            if tool not in self.registry_data['tools']:
                diagnostics.missing_tools.append(tool)
                return None
            
            # Interpolate variables in parameters
            parameters = self._interpolate_variables(
                step_data.get('parameters', {}),
                exec_request,
                diagnostics
            )
            
            step = ExecutionStep(
                step_id=step_id,
                action=step_data.get('action', ''),
                tool=tool,
                parameters=parameters,
                dependencies=step_data.get('depends_on', []),
                timeout=step_data.get('timeout', self.registry_data['tools'][tool]['estimated_duration']),
                required_role=step_data.get('required_role'),
                validation_rules=step_data.get('validation_rules', []),
                retry_policy=step_data.get('retry_policy', {'max_attempts': 3, 'backoff': 'exponential'})
            )
            
            return step
            
        except Exception as e:
            diagnostics.validation_warnings.append(f"Step compilation error: {str(e)}")
            return None
    
    def _interpolate_variables(
        self, 
        parameters: Dict[str, Any], 
        exec_request: ExecutionRequest,
        diagnostics: CompilationDiagnostics
    ) -> Dict[str, Any]:
        """Interpolate variables like ${target.case_id}"""
        
        def interpolate_value(value):
            if isinstance(value, str) and '${' in value:
                # Simple variable interpolation
                import re
                variables = re.findall(r'\$\{([^}]+)\}', value)
                
                for var in variables:
                    if var.startswith('target.'):
                        key = var[7:]  # Remove 'target.'
                        if key in exec_request.target:
                            value = value.replace(f'${{{var}}}', str(exec_request.target[key]))
                        else:
                            diagnostics.missing_variables.append(var)
                    elif var in exec_request.variables:
                        value = value.replace(f'${{{var}}}', str(exec_request.variables[var]))
                    else:
                        diagnostics.missing_variables.append(var)
            
            elif isinstance(value, dict):
                return {k: interpolate_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [interpolate_value(item) for item in value]
                
            return value
        
        return {k: interpolate_value(v) for k, v in parameters.items()}
    
    def _detect_cycles(self, steps: List[ExecutionStep], diagnostics: CompilationDiagnostics) -> bool:
        """Detect dependency cycles using DFS"""
        
        def has_cycle(step_id, visited, rec_stack, adj_list):
            visited.add(step_id)
            rec_stack.add(step_id)
            
            for neighbor in adj_list.get(step_id, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, adj_list):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(step_id)
            return False
        
        # Build adjacency list
        adj_list = {}
        all_steps = {step.step_id for step in steps}
        
        for step in steps:
            adj_list[step.step_id] = [dep for dep in step.dependencies if dep in all_steps]
        
        visited = set()
        rec_stack = set()
        
        for step_id in all_steps:
            if step_id not in visited:
                if has_cycle(step_id, visited, rec_stack, adj_list):
                    diagnostics.cycle_errors.append(f"Dependency cycle detected involving {step_id}")
                    return True
        
        return False
    
    def _calculate_execution_order(self, steps: List[ExecutionStep]) -> List[str]:
        """Calculate topological order for execution"""
        
        # Build adjacency list and in-degree count
        adj_list = {}
        in_degree = {}
        all_steps = {step.step_id for step in steps}
        
        for step in steps:
            adj_list[step.step_id] = []
            in_degree[step.step_id] = 0
        
        for step in steps:
            for dep in step.dependencies:
                if dep in all_steps:
                    adj_list[dep].append(step.step_id)
                    in_degree[step.step_id] += 1
        
        # Kahn's algorithm
        queue = [step_id for step_id in all_steps if in_degree[step_id] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _calculate_execution_groups(self, steps: List[ExecutionStep]) -> List[List[str]]:
        """Calculate parallel execution groups"""
        groups = []
        processed = set()
        step_map = {step.step_id: step for step in steps}
        
        while len(processed) < len(steps):
            current_group = []
            
            for step in steps:
                if step.step_id in processed:
                    continue
                    
                # Check if all dependencies are processed
                if all(dep in processed or dep not in step_map for dep in step.dependencies):
                    current_group.append(step.step_id)
            
            if current_group:
                groups.append(current_group)
                processed.update(current_group)
            else:
                # Fallback to avoid infinite loop
                remaining = [step.step_id for step in steps if step.step_id not in processed]
                if remaining:
                    groups.append([remaining[0]])
                    processed.add(remaining[0])
        
        return groups
    
    def _validate_roles_and_scopes(
        self, 
        steps: List[ExecutionStep], 
        exec_request: ExecutionRequest,
        diagnostics: CompilationDiagnostics
    ):
        """Validate role permissions and scopes"""
        
        user_role = exec_request.role
        user_scopes = self.registry_data['roles'].get(user_role, [])
        
        for step in steps:
            # Check required role
            if step.required_role and step.required_role != user_role and user_role != 'admin':
                diagnostics.role_violations.append(
                    f"Step {step.step_id} requires role {step.required_role}, but user has {user_role}"
                )
            
            # Check tool scopes
            tool_info = self.registry_data['tools'].get(step.tool, {})
            required_scopes = tool_info.get('scope_required', [])
            
            for scope in required_scopes:
                if scope not in user_scopes and '*' not in user_scopes:
                    diagnostics.missing_scopes.append(f"Step {step.step_id} requires scope {scope}")
    
    def _calculate_budget_estimate(
        self, 
        steps: List[ExecutionStep],
        diagnostics: CompilationDiagnostics
    ) -> Dict[str, float]:
        """Calculate resource budget estimates"""
        
        total_duration = sum(step.timeout for step in steps)
        parallel_duration = max(
            sum(self.registry_data['tools'].get(step_map[step_id].tool, {}).get('estimated_duration', 60) 
                for step_id in group)
            for group in self._calculate_execution_groups(steps)
        ) if steps else 0
        
        # Warn about high duration
        if total_duration > 3600:  # 1 hour
            diagnostics.budget_warnings.append(f"High total duration: {total_duration} seconds")
        
        step_map = {step.step_id: step for step in steps}
        
        return {
            'total_duration_seconds': total_duration,
            'parallel_duration_seconds': parallel_duration,
            'estimated_cost_usd': total_duration * 0.001,  # $0.001 per second
            'step_count': len(steps)
        }

# Global instance
chitty_sop_compiler = ChittySOPCompiler()