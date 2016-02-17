{
    "name" : "distributed_count",
    "label": "Distributed count of string in file",
    "dag": {
        "nodes": {
            "split":   "steps.split.Split",
            "count":   "steps.count.Count",
            "collect": "steps.collect.Collect"
        },
        "edges": [
            {
                "from"     : "split",
                "to"       : "count",
                "bindings" : { "count.input_files" : "split.output_files" }
            },
            {
                "from"     : "count",
                "to"       : "collect",
                "bindings" : { "collect.input_files" : "count.output_files" }
            }
        ]
    },
    "config" : {
	    "steps": {
            	"split": {
                	"nchunks": 100,
                	"suffix": ".txt"
            	}
	    }
    }
}
