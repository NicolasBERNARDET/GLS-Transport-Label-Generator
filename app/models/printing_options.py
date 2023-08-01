from app.models.return_labels import ReturnLabels


class PrintingOptions:
    def __init__(self, return_labels: ReturnLabels) -> None:
        self.ReturnLabels = return_labels
