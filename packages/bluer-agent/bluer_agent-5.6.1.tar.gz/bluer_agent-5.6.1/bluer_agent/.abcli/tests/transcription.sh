#! /usr/bin/env bash

function test_bluer_agent_transcription() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_agent_transcription_validate \
        download,filename=farsi.wav,language=fa,verbose \
        $BLUER_AGENT_TRANSCRIPTION_TEST_OBJECT
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_ai_eval ,$options \
        bluer_agent_transcription_validate \
        download,filename=english.wav,language=env,verbose \
        $BLUER_AGENT_TRANSCRIPTION_TEST_OBJECT
}
