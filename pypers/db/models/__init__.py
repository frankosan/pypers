from .stub import PipelineDbStub
from .mongo import PipelineDb


db_models = {
    "STUB_DB"     : PipelineDbStub,
    "MONGO_DB"    : PipelineDb
}
