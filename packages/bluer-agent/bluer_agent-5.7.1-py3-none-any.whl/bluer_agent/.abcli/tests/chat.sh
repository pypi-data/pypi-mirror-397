#! /usr/bin/env bash

function test_bluer_agent_chat() {
    local options=$1

    local object_name=test_bluer_agent_chat-$(bluer_ai_string_timestamp)

    bluer_agent_chat_validate - $object_name
}
