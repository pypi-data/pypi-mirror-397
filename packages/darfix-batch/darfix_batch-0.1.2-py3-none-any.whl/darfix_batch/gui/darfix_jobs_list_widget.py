from darfix_batch.common.gui.jobs_list_widget import JobItem
from darfix_batch.common.gui.jobs_list_widget import JobsListWidget


class DarfixJobListWidget(JobsListWidget):
    @staticmethod
    def jobItemDescription(jobItem: JobItem):
        workflow_parameters = jobItem.getArguments()
        for item in workflow_parameters["inputs"]:
            if item["name"] == "treated_data_dir":
                return item["value"]

        return super().jobItemDescription(jobItem)
