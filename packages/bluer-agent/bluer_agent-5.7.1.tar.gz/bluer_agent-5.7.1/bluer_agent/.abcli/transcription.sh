#! /usr/bin/env bash

function bluer_agent_transcription() {
    local task=$1

    local function_name=bluer_agent_transcription_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m bluer_agent.transcription "$@"
}

bluer_ai_source_caller_suffix_path /transcription
