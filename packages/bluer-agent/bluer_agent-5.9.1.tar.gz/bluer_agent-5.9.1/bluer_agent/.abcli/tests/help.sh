#! /usr/bin/env bash

function test_bluer_agent_help() {
    local options=$1

    local module
    for module in \
        "@agent" \
        "@agent chat" \
        \
        "@agent chat validate" \
        "@agent transcription" \
        "@agent transcription validate" \
        \
        "@agent pypi" \
        "@agent pypi browse" \
        "@agent pypi build" \
        "@agent pypi install" \
        \
        "@agent pytest" \
        \
        "@agent test" \
        "@agent test list" \
        \
        "@ai_agent" \
        \
        "bluer_agent"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1

        bluer_ai_hr
    done

    return 0
}
