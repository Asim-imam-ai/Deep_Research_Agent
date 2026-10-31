from pydantic import BaseModel, Field, model_validator


class StartResearchRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=1000)
    max_analysts: int = Field(3, ge=1, le=8)
    max_num_turns: int = Field(2, ge=1, le=8)


class FeedbackRequest(BaseModel):
    approved: bool
    feedback: str = Field(default="", max_length=5000)

    @model_validator(mode="after")
    def validate_rejection(self):
        if not self.approved and not self.feedback.strip():
            raise ValueError("Feedback is required for rejection")
        return self
