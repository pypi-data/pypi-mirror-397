"""
Workflow API endpoints for lmapp GUI
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import yaml
import aiofiles
from typing import Dict, Any, List

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])

# Workflow templates directory
WORKFLOW_DIR = Path(__file__).parent.parent.parent / "workflows" / "templates"


@router.get("")
async def list_workflows() -> Dict[str, List[Dict[str, Any]]]:
    """List all available workflow templates"""
    workflows = []
    
    if not WORKFLOW_DIR.exists():
        return {"workflows": []}
    
    for yaml_file in WORKFLOW_DIR.glob("*.yaml"):
        try:
            async with aiofiles.open(yaml_file, 'r') as f:
                content = await f.read()
                workflow = yaml.safe_load(content)
                
                # Add metadata
                workflow['id'] = yaml_file.stem
                workflow['filename'] = yaml_file.name
                
                workflows.append(workflow)
        except Exception as e:
            print(f"Failed to load workflow {yaml_file}: {e}")
            continue
    
    return {"workflows": workflows}


@router.post("/execute")
async def execute_workflow_step(step_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single workflow step
    
    Expected step_data:
    {
        "workflow": "workflow_name",
        "step": 0,
        "action": "action_type",
        "prompt": "interpolated_prompt",
        "variables": {...}
    }
    """
    try:
        from ...workflows.actions import execute_action
        from ...workflows.llm_integration import get_llm_backend
        
        action = step_data.get("action")
        prompt = step_data.get("prompt")
        variables = step_data.get("variables", {})
        
        # For LLM actions, use the LLM backend
        llm_actions = [
            "generate_outline", "write_section", "summarize",
            "generate_email", "analyze_document"
        ]
        
        if action in llm_actions:
            llm = get_llm_backend()
            result = llm.generate(prompt)
        else:
            # Use action handler
            result = execute_action(action, prompt, variables)
        
        return {
            "success": True,
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get a specific workflow by ID"""
    workflow_file = WORKFLOW_DIR / f"{workflow_id}.yaml"
    
    if not workflow_file.exists():
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    try:
        async with aiofiles.open(workflow_file, 'r') as f:
            content = await f.read()
            workflow = yaml.safe_load(content)
            workflow['id'] = workflow_id
            workflow['filename'] = workflow_file.name
            return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
