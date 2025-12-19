#! /usr/bin/env bash

function bluer_agent_chat_validate() {
    local options=$1
    local do_upload=$(bluer_ai_option_int "$options" upload 0)
    local verbose=$(bluer_ai_option_int "$options" verbose 1)

    local object_name=$(bluer_ai_clarify_object $2 chat-$(bluer_ai_string_timestamp))
    local chat_filename=$ABCLI_OBJECT_ROOT/$object_name/chat.json

    # https://docs.arvancloud.ir/fa/aiaas/api-usage
    bluer_ai_log "processing..."
    curl --location "$BLUER_AGENT_CHAT_ENDPOINT/chat/completions" \
        --header "Authorization: apikey $BLUER_AGENT_API_KEY" \
        --header 'Content-Type: application/json' \
        --data '{
    "model": "DeepSeek-R1-Distill-Qwen-32b",
    "messages": [
        {"role": "user", "content": "چرا آسمان آبی است؟"}
    ],
    "max_tokens": 3000,
    "temperature": 0.7
    }' >$chat_filename
    [[ $? -ne 0 ]] && return 1

    [[ "$verbose" == 1 ]] &&
        bluer_ai_cat $chat_filename

    bluer_ai_eval - \
        python3 -m bluer_agent.chat \
        post_process \
        --object_name $object_name
    [[ $? -ne 0 ]] && return 1

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload - \
            $object_name

    return 0
}
