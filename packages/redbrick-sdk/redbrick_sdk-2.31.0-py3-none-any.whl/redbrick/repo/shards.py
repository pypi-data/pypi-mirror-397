"""Partial queries to prevent duplication."""

USER_SHARD = """
userId
email
givenName
"""

ORG_INVITE_SHARD = """
email
role
state
idProvider
"""

ORG_MEMBER_SHARD = """
user {
    userId
    email
    givenName
    familyName
    mfaSetup
    lastSeen
    updatedAt
    idProvider
}
role
tags
active
lastSeen
"""


STORAGE_METHOD_SHARD = f"""
orgId
storageId
name
provider
details {{
    ... on S3BucketStorageDetails {{
        bucket
        region
        duration
        access
        roleArn
        endpoint
        accelerate
    }}
    ... on GCSBucketStorageDetails {{
        bucket
    }}
}}
createdBy {{
    {USER_SHARD}
}}
createdAt
deleted
"""

ATTRIBUTE_SHARD = """
name
attrType
attrId
options {
    name
    optionId
    color
    archived
}
archived
parents
hint
defaultValue
"""

WORKSPACE_SHARD = f"""
orgId
workspaceId
name
desc
createdAt
status
metadataSchema {{
    uniqueName
    displayName
    dataType
    options
    required
}}
classificationSchema {{
    {ATTRIBUTE_SHARD}
}}
cohorts {{
    name
    color
    createdBy
    createdAt
}}
"""

STAGE_SHARD = """
stageName
brickName
stageConfig
routing {
    ...on NoRouting {
        placeholder
    }
    ...on NextRouting {
        nextStageName
    }
    ...on MultiRouting {
        stageNames
    }
    ...on BooleanRouting {
        passed
        failed
    }
    ...on FeedbackRouting {
        feedbackStageName
    }
}
"""

OLD_ATTRIBUTE_SHARD = """
name
attrType
whitelist
disabled
"""

OLD_CATEGORY_SHARD = """
name
children {
    name
    classId
    disabled
    children {
        name
        classId
        disabled
        children {
            name
            classId
            disabled
            children {
                name
                classId
                disabled
                children {
                    name
                    classId
                    disabled
                    children {
                        name
                        classId
                        disabled
                    }
                }
            }
        }
    }
}
"""

TAXONOMY_SHARD = f"""
orgId
name
version
createdAt
categories {{
    {OLD_CATEGORY_SHARD}
}}
attributes {{
    {OLD_ATTRIBUTE_SHARD}
}}
taskCategories {{
    {OLD_CATEGORY_SHARD}
}}
taskAttributes {{
    {OLD_ATTRIBUTE_SHARD}
}}
colorMap {{
    name
    color
    classid
    trail
    taskcategory
}}
archived
isNew
taxId
studyClassify {{
    {ATTRIBUTE_SHARD}
}}
seriesClassify {{
    {ATTRIBUTE_SHARD}
}}
instanceClassify {{
    {ATTRIBUTE_SHARD}
}}
objectTypes {{
    category
    classId
    labelType
    attributes {{
        {ATTRIBUTE_SHARD}
    }}
    color
    archived
    parents
    hint
}}
"""


def project_shard(with_stages: bool = False, with_taxonomy: bool = False) -> str:
    """Return the project shard."""
    return f"""
        orgId
        projectId
        name
        desc
        status
        tdType
        taxonomy {{
            {TAXONOMY_SHARD if with_taxonomy else "name"}
        }}
        projectUrl
        createdAt
        updatedAt
        consensusSettings {{
            enabled
        }}
        workspace {{
            workspaceId
        }}
        {f"stages {{ {STAGE_SHARD} }}" if with_stages else ""}
    """


def task_data_shard(presigned: bool = False) -> str:
    """Return the task data shard."""
    return f"""
        tdId
        createdAt
        createdByEntity {{
            {USER_SHARD}
        }}
        labelsData(interpolate: true)
        labelsDataPath(presigned: {"true" if presigned else "false"})
        labelsStorage {{
            storageId
        }}
        labelsMap(presigned: {"true" if presigned else "false"}) {{
            seriesIndex
            imageIndex
            labelName
        }}
    """


NORMAL_TASK_SHARD = f"""
    ... on LabelingTask {{
        state
        assignedTo {{
            {USER_SHARD}
        }}
    }}
"""

CONSENSUS_TASK_SHARD = f"""
    ... on LabelingTask {{
        state
        assignedTo {{
            {USER_SHARD}
        }}
        taskData {{
            {task_data_shard()}
        }}
        subTasks {{
            state
            assignedTo {{
                {USER_SHARD}
            }}
            taskData {{
                {task_data_shard()}
            }}
        }}
        overallConsensusScore
        consensusInfo {{
            user {{
                {USER_SHARD}
            }}
            taskData {{
                {task_data_shard()}
            }}
            scores {{
                user {{
                    {USER_SHARD}
                }}
                score
            }}
        }}
    }}
"""

TASK_COMMENT_SHARD = f"""
    commentId
    createdBy {{
        {USER_SHARD}
    }}
    textVal
    createdAt
    stageName
    issueComment
    issueResolved
    labelEntityLabelId
    replies {{
        commentId
        createdBy {{
            {USER_SHARD}
        }}
        textVal
        createdAt
        stageName
        issueComment
        issueResolved
        labelEntityLabelId
        pin {{
            pinId
            pointX
            pointY
            pointZ
            frameIndex
            volumeIndex
        }}
    }}
    pin {{
        pinId
        pointX
        pointY
        pointZ
        frameIndex
        volumeIndex
    }}
"""


def datapoint_shard(raw_items: bool, presigned_items: bool) -> str:
    """Return the datapoint shard."""
    return f"""
        dpId
        name
        {"items(presigned: false)" if raw_items else ""}
        {"itemsPresigned:items(presigned: true)" if presigned_items else ""}
        createdAt
        createdByEntity {{
            {USER_SHARD}
        }}
        metaData
        seriesInfo {{
            name
            itemsIndices
            dataType
            metaData
            imageHeaders
            localToWorldTransform
        }}
        heatMaps {{
            seriesIndex
            seriesName
            name
            item
            preset
            dataRange
            opacityPoints
            opacityPoints3d
            rgbPoints
        }}
        transforms {{
            seriesIndex
            transform
        }}
        centerline {{
            seriesIndex
            name
            centerline
        }}
        storageMethod {{
            storageId
        }}
        attributes
        archived
        cohorts {{
            name
        }}
    """


def task_shard(presigned_items: bool, with_consensus: bool) -> str:
    """Return the task shard for the router query."""
    return f"""
        taskId
        dpId
        currentStageName
        priority
        {f"currentStageSubTask(consensus: true) {{ {CONSENSUS_TASK_SHARD} }}" if with_consensus else f"currentStageSubTask {{ {NORMAL_TASK_SHARD} }}"}
        datapoint {{
            {datapoint_shard(True, presigned_items)}
        }}
        latestTaskData {{
            {task_data_shard()}
        }}
    """


def router_task_shard() -> str:
    """Return router task shard for events query."""
    return f"""
        taskId
        currentStageName
        datapoint {{
            {datapoint_shard(True, False)}
        }}
        priority
        genericEvents {{
            __typename
            ... on TaskEvent {{
                eventId
                createdAt
                updatedBy
                createEvent {{
                    currentStageName
                    isGroundTruth
                    priority
                }}
                inputEvent {{
                    currentStageName
                    overallConsensusScore
                    priority
                    consensusInfo {{
                        user {{ {USER_SHARD} }}
                        taskData {{
                            tdId
                        }}
                        scores {{
                            user {{ {USER_SHARD} }}
                            score
                        }}
                    }}
                }}
                outputEvent {{
                    currentStageName
                    cycleCount
                    outputBool
                    nextStageName
                    timeSpentMs
                    extraData
                    multiLabels {{
                        user {{ {USER_SHARD} }}
                        taskData {{
                            tdId
                        }}
                    }}
                }}
                taskData {{
                    tdId
                    stageName
                    createdBy
                }}
            }}
            ... on Comment {{
                {TASK_COMMENT_SHARD}
            }}
            ... on TaskStateChanges {{
                stageNameAfter: stageName
                assignedAtAfter
                createdAt
                updatedBy
                statusBefore
                statusAfter
                assignedToBeforeEntity {{
                    {USER_SHARD}
                }}
                assignedToAfterEntity {{
                    {USER_SHARD}
                }}
                consensusAssigneesBefore
                consensusAssigneesAfter
                consensusStatusesBefore
                consensusStatusesAfter
                reviewResultBefore
                reviewResultAfter
            }}
        }}
    """
