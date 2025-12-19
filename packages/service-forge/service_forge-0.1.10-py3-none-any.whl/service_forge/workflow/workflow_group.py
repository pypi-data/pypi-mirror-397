from service_forge.workflow.workflow import Workflow

class WorkflowGroup:
    def __init__(self, workflows: list[Workflow], main_workflow_name: str = "main") -> None:
        self.workflows = workflows
        self.main_workflow_name = main_workflow_name

    def add_workflow(self, workflow: Workflow) -> None:
        self.workflows.append(workflow)

    def get_workflow(self, name: str) -> Workflow | None:
        for workflow in self.workflows:
            if workflow.name == name:
                return workflow
        return None

    def get_main_workflow(self) -> Workflow:
        return self.get_workflow(self.main_workflow_name)

    async def run(self, name: str = None) -> None:
        if name is None:
            workflow = self.get_main_workflow()
        else:
            workflow = self.get_workflow(name)
        if workflow is None:
            raise ValueError(f"Workflow with name {name} not found in workflow group.")
        await workflow.run()