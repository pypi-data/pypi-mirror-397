#! /usr/bin/env bash

function bluer_agent_transcription_validate() {
    local options=$1
    local do_download=$(bluer_ai_option_int "$options" download 1)
    local do_install=$(bluer_ai_option_int "$options" install 0)
    local do_record=$(bluer_ai_option_int "$options" record 0)
    local do_play=$(bluer_ai_option_int "$options" play $do_record)
    local do_upload=$(bluer_ai_option_int "$options" upload 0)
    local language=$(bluer_ai_option "$options" language fa)
    local filename=$(bluer_ai_option "$options" filename audio-$(bluer_ai_string_timestamp).wav)
    local verbose=$(bluer_ai_option_int "$options" verbose 1)

    if [[ "$do_install" == 1 ]]; then
        brew install sox
    fi

    local object_name=$(bluer_ai_clarify_object $2 transcription-$(bluer_ai_string_timestamp))

    [[ "$do_download" == 1 ]] &&
        bluer_objects_download \
            filename=$filename \
            $object_name

    local voice_filename=$ABCLI_OBJECT_ROOT/$object_name/$filename
    local transcript_filename=$ABCLI_OBJECT_ROOT/$object_name/transcript.json

    if [[ "$do_record" == 1 ]]; then
        bluer_ai_log "recording audio ... (^C to end)"

        bluer_ai_eval - \
            rec \
            -r 48000 \
            -c 1 \
            $voice_filename
        [[ $? -ne 0 ]] && return 1
    fi

    if [[ ! -f "$voice_filename" ]]; then
        bluer_ai_log_error "voice file not found: $voice_filename"
        return 1
    fi

    if [[ "$do_play" == 1 ]]; then
        bluer_ai_eval - \
            afplay $voice_filename
        [[ $? -ne 0 ]] && return 1
    fi

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload \
            filename=$filename \
            $object_name

    # https://docs.arvancloud.ir/fa/aiaas/api-usage
    bluer_ai_log "processing..."
    curl --location "$BLUER_AGENT_TRANSCRIPTION_ENDPOINT/audio/transcriptions" \
        --header "Authorization: apikey $BLUER_AGENT_API_KEY" \
        --form "model=whisper-1" \
        --form "file=@$voice_filename" \
        --form "language=$language" >$transcript_filename
    [[ $? -ne 0 ]] && return 1

    [[ "$verbose" == 1 ]] &&
        bluer_ai_cat $transcript_filename

    bluer_ai_eval - \
        python3 -m bluer_agent.transcription \
        post_process \
        --object_name $object_name \
        --filename $voice_filename \
        --language $language
}
