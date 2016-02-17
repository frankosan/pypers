{
    "comment" : [ 
        "This is just an example pipeline JSON to make it easier.",
        "Remove this section to get started                      "
    ],
    "name" : "unique_id",
    "label": "Label shown in flock",
    "dag": {
        "nodes": {
            "name": "stepclass"
        },
        "edges": [
            {
                "from"     : "stepclass",
                "to"       : "",
                "bindings" : { "" : "stepclass.okey" }
            }
        ]
    },
    "config" : {
	"steps": {
	    "comment": ["This can be used to set default parameters to the steps."]
	}
    }
}
