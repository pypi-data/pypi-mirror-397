import aioboto3

from ..settings import WORKFLOW_TABLE_NAME


class WorkflowTracker:
    workflow: dict
    table = WORKFLOW_TABLE_NAME

    @staticmethod
    async def track(workflow_id: str) -> "WorkflowTracker":
        workflow_tracker = WorkflowTracker()
        workflow_tracker.workflow = await WorkflowTracker.get_workflow(workflow_id)  # type: ignore

        if workflow_tracker.workflow is None:
            # create new workflow
            workflow_tracker.workflow = {
                "id": workflow_id,
                "warnings": [],
                "errors": [],
            }

        return workflow_tracker

    @staticmethod
    async def get_workflow(workflow_id: str) -> dict | None:
        async with aioboto3.Session().resource("dynamodb") as dynamo:
            table = await dynamo.Table(WorkflowTracker.table)
            response = await table.get_item(Key={"id": workflow_id})

        return response.get("Item")

    async def start_step(self, step: str):
        self.workflow[step] = "started"
        await self._save()

    async def complete_step(self, step: str, warnings: list | None = None):
        self.workflow[step] = "completed"
        if warnings:
            self.workflow["warnings"].extend(warnings)
        await self._save()

    async def fail_step(self, step: str, errors: list | None = None):
        self.workflow[step] = "failed"
        if errors:
            self.workflow["errors"].extend(errors)
        await self._save()

    async def _save(self):
        async with aioboto3.Session().resource("dynamodb") as dynamo:
            table = await dynamo.Table(self.table)
            await table.put_item(Item=self.workflow)
