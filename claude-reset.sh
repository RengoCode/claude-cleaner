#!/usr/bin/env bash
# ==============================================================================
# Claude Anti-Ban & Telemetry Cleaner
# Universal native Bash reset & privacy utility for macOS & Linux (0 dependencies)
# Bilingual support: English & Russian
# ==============================================================================

set -e

# --- Configuration & Paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT_DIR="${HOME}/.claude-cleaner/backups"
CONFIG_DIR="${HOME}/.claude-cleaner"
mkdir -p "${BACKUP_ROOT_DIR}" "${CONFIG_DIR}"

LANG_CONFIG_FILE="${CONFIG_DIR}/language.txt"

# Detect OS
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
    Darwin*)
        PLATFORM="macos"
        APP_DATA_CLAUDE="${HOME}/Library/Application Support/Claude"
        ;;
    Linux*|*)
        PLATFORM="linux"
        APP_DATA_CLAUDE="${HOME}/.config/Claude"
        ;;
esac

# CLI Paths
CLI_DIR="${HOME}/.claude"
CLI_CONFIG_1="${HOME}/.claude.json"
CLI_CONFIG_2="${CLI_DIR}/.claude.json"
CLI_TELEMETRY="${CLI_DIR}/telemetry"
CLI_STATS_CACHE="${CLI_DIR}/stats-cache.json"
CLI_DAEMON_STATUS="${CLI_DIR}/daemon-auth-status.json"
CLI_DAEMON_COOLDOWN="${CLI_DIR}/daemon-auth-cooldown"

# Desktop Paths
DESKTOP_ANT_DID="${APP_DATA_CLAUDE}/ant-did"
DESKTOP_ANT_REGISTRY="${APP_DATA_CLAUDE}/ant-device-registry.json"
DESKTOP_CONFIG="${APP_DATA_CLAUDE}/config.json"
DESKTOP_LOCAL_STATE="${APP_DATA_CLAUDE}/Local State"
DESKTOP_PLAN_USAGE="${APP_DATA_CLAUDE}/plan-usage-history.json"
DESKTOP_PERF_DB="${APP_DATA_CLAUDE}/declarative_performance_observer.db"
DESKTOP_PERF_JOURNAL="${APP_DATA_CLAUDE}/declarative_performance_observer.db-journal"
DESKTOP_CRASHPAD="${APP_DATA_CLAUDE}/Crashpad"
DESKTOP_CCD_IDS="${APP_DATA_CLAUDE}/ccd-ids.json"
DESKTOP_BRIDGE_STATE="${APP_DATA_CLAUDE}/bridge-state.json"
DESKTOP_REMOTE_CONTROL="${APP_DATA_CLAUDE}/remote-control-state.json"
DESKTOP_BUDDY_TOKENS="${APP_DATA_CLAUDE}/buddy-tokens.json"
DESKTOP_SESSIONS_DIR="${APP_DATA_CLAUDE}/claude-code-sessions"
DESKTOP_SENTRY_DIR="${APP_DATA_CLAUDE}/sentry"
DESKTOP_LOGS_DIR="${APP_DATA_CLAUDE}/logs"

# ANSI Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# Parse Command-line arguments
AUTO_MODE=false
WIPE_SESSIONS=false
DRY_RUN=false
ARG_LANG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --auto|-a)
            AUTO_MODE=true
            shift
            ;;
        --wipe-sessions|--full)
            WIPE_SESSIONS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --lang)
            ARG_LANG="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./claude-reset.sh [options]"
            echo "  --auto, -a         Run safe reset without interactive prompts"
            echo "  --full             Factory reset (resets IDs AND removes saved local sessions)"
            echo "  --dry-run          Simulate reset operations without modifying files"
            echo "  --lang <ru|en>     Force UI language"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Language resolution
if [[ -n "${ARG_LANG}" ]]; then
    ACTIVE_LANG="${ARG_LANG}"
    echo "${ACTIVE_LANG}" > "${LANG_CONFIG_FILE}" 2>/dev/null || true
elif [[ -f "${LANG_CONFIG_FILE}" ]]; then
    SAVED_LANG="$(cat "${LANG_CONFIG_FILE}" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')"
    if [[ "${SAVED_LANG}" == "ru" || "${SAVED_LANG}" == "en" ]]; then
        ACTIVE_LANG="${SAVED_LANG}"
    else
        ACTIVE_LANG="en"
    fi
else
    SYS_LANG="$(echo "${LANG:-${LC_ALL:-en}}" | cut -c1-2 | tr '[:upper:]' '[:lower:]')"
    if [[ "${SYS_LANG}" == "ru" ]]; then
        ACTIVE_LANG="ru"
    else
        ACTIVE_LANG="en"
    fi
fi

# Helpers
random_hex_64() {
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -hex 32
    else
        LC_ALL=C tr -dc 'a-f0-9' < /dev/urandom | head -c 64
    fi
}

random_uuid() {
    if command -v uuidgen >/dev/null 2>&1; then
        uuidgen | tr '[:upper:]' '[:lower:]'
    elif [[ -r /proc/sys/kernel/random/uuid ]]; then
        cat /proc/sys/kernel/random/uuid
    else
        h="$(random_hex_64)"
        printf "%s-%s-%s-%s-%s\n" "${h:0:8}" "${h:8:4}" "${h:12:4}" "${h:16:4}" "${h:20:12}"
    fi
}

stop_claude_processes() {
    # Strictly target exact process names, avoiding self-termination
    pkill -x "Claude" 2>/dev/null || true
    pkill -x "claude" 2>/dev/null || true
    sleep 1
    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${GREEN}[+] Проверены и завершены активные процессы Claude.${NC}"
    else
        echo -e "${GREEN}[+] Checked and terminated any running Claude processes.${NC}"
    fi
}

create_backup() {
    local tag="${1:-backup}"
    local timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
    local target_dir="${BACKUP_ROOT_DIR}/backup_${timestamp}_${tag}"
    mkdir -p "${target_dir}"

    if [[ -f "${CLI_CONFIG_1}" ]]; then cp "${CLI_CONFIG_1}" "${target_dir}/user_claude.json"; fi
    if [[ -f "${CLI_CONFIG_2}" ]]; then cp "${CLI_CONFIG_2}" "${target_dir}/nested_claude.json"; fi
    if [[ -f "${CLI_STATS_CACHE}" ]]; then cp "${CLI_STATS_CACHE}" "${target_dir}/cli_stats_cache.json"; fi

    if [[ -d "${APP_DATA_CLAUDE}" ]]; then
        local desktop_bak="${target_dir}/Claude_AppData"
        mkdir -p "${desktop_bak}"
        for f in "${DESKTOP_ANT_DID}" "${DESKTOP_ANT_REGISTRY}" "${DESKTOP_CONFIG}" \
                 "${DESKTOP_LOCAL_STATE}" "${DESKTOP_PLAN_USAGE}" "${DESKTOP_CCD_IDS}" \
                 "${DESKTOP_BRIDGE_STATE}" "${DESKTOP_REMOTE_CONTROL}" "${DESKTOP_BUDDY_TOKENS}"; do
            if [[ -f "${f}" ]]; then cp "${f}" "${desktop_bak}/"; fi
        done
        if [[ -d "${DESKTOP_SESSIONS_DIR}" ]]; then
            cp -r "${DESKTOP_SESSIONS_DIR}" "${desktop_bak}/"
        fi
    fi

    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${GREEN}[+] Резервная копия сохранена в: ${target_dir}${NC}"
    else
        echo -e "${GREEN}[+] Safety backup saved at: ${target_dir}${NC}"
    fi
    echo "${target_dir}"
}

restore_backup() {
    clear
    local backups=($(ls -td "${BACKUP_ROOT_DIR}"/backup_* 2>/dev/null || true))
    if [[ ${#backups[@]} -eq 0 ]]; then
        echo -e "${RED}[-] No backups found in ${BACKUP_ROOT_DIR}${NC}"
        read -r -p "Press Enter to continue..."
        return
    fi

    echo -e "${CYAN}Available backups / Доступные резервные копии:${NC}"
    for i in "${!backups[@]}"; do
        echo -e "  [${YELLOW}$((i+1))${NC}] $(basename "${backups[$i]}")"
    done
    echo -e "  [${GRAY}0${NC}] Cancel / Отмена\n"

    read -r -p "Select backup number / Выберите номер для восстановления: " choice
    if [[ "${choice}" == "0" || -z "${choice}" ]]; then return; fi

    local idx=$((choice - 1))
    if [[ $idx -lt 0 || $idx -ge ${#backups[@]} ]]; then
        echo -e "${RED}[-] Invalid choice.${NC}"
        read -r -p "Press Enter to continue..."
        return
    fi

    local selected="${backups[$idx]}"
    stop_claude_processes

    echo -e "${YELLOW}[*] Restoring from ${selected}...${NC}"
    if [[ -f "${selected}/user_claude.json" ]]; then cp "${selected}/user_claude.json" "${CLI_CONFIG_1}"; fi
    if [[ -f "${selected}/nested_claude.json" ]]; then cp "${selected}/nested_claude.json" "${CLI_CONFIG_2}"; fi
    if [[ -f "${selected}/cli_stats_cache.json" ]]; then cp "${selected}/cli_stats_cache.json" "${CLI_STATS_CACHE}"; fi

    if [[ -d "${selected}/Claude_AppData" ]]; then
        mkdir -p "${APP_DATA_CLAUDE}"
        for f in "${selected}/Claude_AppData"/*; do
            if [[ -f "${f}" ]]; then cp "${f}" "${APP_DATA_CLAUDE}/"; fi
        done
        if [[ -d "${selected}/Claude_AppData/claude-code-sessions" ]]; then
            cp -r "${selected}/Claude_AppData/claude-code-sessions" "${APP_DATA_CLAUDE}/"
        fi
    fi

    echo -e "\n${GREEN}[+] Restoration completed successfully! / Восстановление успешно завершено!${NC}\n"
    read -r -p "Press Enter to continue..."
}

view_identifiers() {
    clear
    echo -e "${CYAN}======================================================================${NC}"
    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${YELLOW}           ТЕКУЩИЕ ИДЕНТИФИКАТОРЫ И ТЕЛЕМЕТРИЯ CLAUDE${NC}"
    else
        echo -e "${YELLOW}           CURRENT CLAUDE IDENTIFIERS & TELEMETRY STATUS${NC}"
    fi
    echo -e "${CYAN}======================================================================${NC}\n"

    echo -e "${WHITE}--- Claude Code CLI (${CLI_CONFIG_1}) ---${NC}"
    if [[ -f "${CLI_CONFIG_1}" ]]; then
        echo -n "  machineID:   "
        grep -o '"machineID"[[:space:]]*:[[:space:]]*"[^"]*"' "${CLI_CONFIG_1}" 2>/dev/null | cut -d'"' -f4 || echo "none"
        echo -n "  userID:      "
        grep -o '"userID"[[:space:]]*:[[:space:]]*"[^"]*"' "${CLI_CONFIG_1}" 2>/dev/null | cut -d'"' -f4 || echo "none"
        echo -n "  anonymousId: "
        grep -o '"anonymousId"[[:space:]]*:[[:space:]]*"[^"]*"' "${CLI_CONFIG_1}" 2>/dev/null | cut -d'"' -f4 || echo "none"
    else
        echo "  [Not found / Не найден]"
    fi

    echo -e "\n${WHITE}--- Claude Desktop (${APP_DATA_CLAUDE}) ---${NC}"
    if [[ -f "${DESKTOP_ANT_DID}" ]]; then
        echo "  ant-did: $(cat "${DESKTOP_ANT_DID}" 2>/dev/null | head -c 40)..."
    else
        echo "  ant-did: [None - clean state / Отсутствует - чистое состояние]"
    fi

    if [[ -f "${DESKTOP_ANT_REGISTRY}" ]]; then
        echo "  ant-device-registry: [PRESENT / ОБНАРУЖЕН - содержит аппаратный хеш]"
    else
        echo "  ant-device-registry: [Not present / Отсутствует]"
    fi

    if [[ -f "${DESKTOP_PLAN_USAGE}" ]]; then
        local psize=$(wc -c < "${DESKTOP_PLAN_USAGE}" 2>/dev/null || echo 0)
        echo "  plan-usage-history: ${psize} bytes [История сессий и расхода тарифа]"
    fi

    if [[ -d "${DESKTOP_SESSIONS_DIR}" ]]; then
        local scount=$(find "${DESKTOP_SESSIONS_DIR}" -type f 2>/dev/null | wc -l || echo 0)
        echo -e "  Saved sessions: ${GREEN}${scount} files (PRESERVED / СОХРАНЯЮТСЯ)${NC}"
    fi

    echo ""
    read -r -p "Press Enter to continue / Нажмите Enter..."
}

perform_reset() {
    clear
    echo -e "${CYAN}======================================================================${NC}"
    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${YELLOW}       CLAUDE ANTI-BAN & СБРОС ИДЕНТИФИКАТОРОВ УСТРОЙСТВА${NC}"
        echo -e "${WHITE}    Сброс ID железа, глубокой телеметрии и защита от привязки аккаунтов${NC}"
    else
        echo -e "${YELLOW}           CLAUDE ANTI-BAN & DEVICE ID RESET UTILITY${NC}"
        echo -e "${WHITE}    Reset Hardware IDs, Deep Telemetry & Account Linkages${NC}"
    fi
    echo -e "${CYAN}======================================================================${NC}\n"

    if [[ "${DRY_RUN}" == true ]]; then
        echo -e "${YELLOW}[DRY-RUN MODE] Changes will not be written to disk.${NC}\n"
    fi

    # 1. Stop processes
    if [[ "${DRY_RUN}" == false ]]; then
        stop_claude_processes
    fi

    # 2. Safety Backup
    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${CYAN}[1/6] Создание защитной резервной копии...${NC}"
    else
        echo -e "${CYAN}[1/6] Creating safety backup...${NC}"
    fi
    if [[ "${DRY_RUN}" == false ]]; then
        create_backup "pre-reset" >/dev/null
    fi

    # 3. CLI Config Reset
    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${CYAN}[2/6] Сброс аппаратных ID и телеметрии Claude CLI...${NC}"
    else
        echo -e "${CYAN}[2/6] Resetting CLI hardware IDs & telemetry...${NC}"
    fi

    for cfg in "${CLI_CONFIG_1}" "${CLI_CONFIG_2}"; do
        if [[ -f "${cfg}" && "${DRY_RUN}" == false ]]; then
            new_mid="$(random_hex_64)"
            new_uid="$(random_hex_64)"
            new_anon="claudecode_${new_mid:0:32}"

            # Replace values in-place using sed (portable across Linux and macOS)
            if [[ "${PLATFORM}" == "macos" ]]; then
                sed -i '' -E "s/(\"machineID\"[[:space:]]*:[[:space:]]*)\"[^\"]+\"/\1\"${new_mid}\"/g" "${cfg}" 2>/dev/null || true
                sed -i '' -E "s/(\"userID\"[[:space:]]*:[[:space:]]*)\"[^\"]+\"/\1\"${new_uid}\"/g" "${cfg}" 2>/dev/null || true
                sed -i '' -E "s/(\"anonymousId\"[[:space:]]*:[[:space:]]*)\"[^\"]+\"/\1\"${new_anon}\"/g" "${cfg}" 2>/dev/null || true
            else
                sed -i -E "s/(\"machineID\"[[:space:]]*:[[:space:]]*)\"[^\"]+\"/\1\"${new_mid}\"/g" "${cfg}" 2>/dev/null || true
                sed -i -E "s/(\"userID\"[[:space:]]*:[[:space:]]*)\"[^\"]+\"/\1\"${new_uid}\"/g" "${cfg}" 2>/dev/null || true
                sed -i -E "s/(\"anonymousId\"[[:space:]]*:[[:space:]]*)\"[^\"]+\"/\1\"${new_anon}\"/g" "${cfg}" 2>/dev/null || true
            fi
            echo -e "${GREEN}  [v] Reset IDs in $(basename "${cfg}") -> machineID: ${new_mid:0:16}...${NC}"
        fi
    done

    # Clean CLI telemetry files
    if [[ "${DRY_RUN}" == false ]]; then
        rm -f "${CLI_TELEMETRY}"/1p_failed_events.*.json 2>/dev/null || true
        rm -f "${CLI_DAEMON_STATUS}" "${CLI_DAEMON_COOLDOWN}" 2>/dev/null || true
        if [[ -f "${CLI_STATS_CACHE}" ]]; then
            echo '{"version":4,"dailyActivity":[]}' > "${CLI_STATS_CACHE}"
        fi
    fi

    # 4. Desktop Reset
    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${CYAN}[3/6] Сброс привязок десктопного приложения Claude...${NC}"
    else
        echo -e "${CYAN}[3/6] Resetting Desktop application device binding...${NC}"
    fi

    if [[ -d "${APP_DATA_CLAUDE}" && "${DRY_RUN}" == false ]]; then
        rm -f "${DESKTOP_ANT_DID}" 2>/dev/null || true
        echo -e "${GREEN}  [v] Removed ant-did (Claude will generate fresh device token).${NC}"

        if [[ -f "${DESKTOP_ANT_REGISTRY}" ]]; then
            new_reg_id="$(random_uuid)"
            echo "{\"deviceId\":\"${new_reg_id}\"}" > "${DESKTOP_ANT_REGISTRY}"
            echo -e "${GREEN}  [v] Spoofed ant-device-registry.json with new device UUID.${NC}"
        fi

        for f in "${DESKTOP_CCD_IDS}" "${DESKTOP_BRIDGE_STATE}" "${DESKTOP_REMOTE_CONTROL}" "${DESKTOP_BUDDY_TOKENS}"; do
            rm -f "${f}" 2>/dev/null || true
        done

        # 5. Sanitize config.json
        if [[ "${ACTIVE_LANG}" == "ru" ]]; then
            echo -e "${CYAN}[4/6] Очистка config.json и телеметрии сессий...${NC}"
        else
            echo -e "${CYAN}[4/6] Sanitizing config.json & session telemetry...${NC}"
        fi

        if [[ -f "${DESKTOP_CONFIG}" ]]; then
            if [[ "${PLATFORM}" == "macos" ]]; then
                sed -i '' -E 's/"activeOrgId"[[:space:]]*:[[:space:]]*"[^"]*"/"activeOrgId":""/g' "${DESKTOP_CONFIG}" 2>/dev/null || true
                sed -i '' -E 's/"lastActiveAccount"[[:space:]]*:[[:space:]]*"[^"]*"/"lastActiveAccount":""/g' "${DESKTOP_CONFIG}" 2>/dev/null || true
                sed -i '' -E 's/"sentryToken"[[:space:]]*:[[:space:]]*"[^"]*"/"sentryToken":""/g' "${DESKTOP_CONFIG}" 2>/dev/null || true
            else
                sed -i -E 's/"activeOrgId"[[:space:]]*:[[:space:]]*"[^"]*"/"activeOrgId":""/g' "${DESKTOP_CONFIG}" 2>/dev/null || true
                sed -i -E 's/"lastActiveAccount"[[:space:]]*:[[:space:]]*"[^"]*"/"lastActiveAccount":""/g' "${DESKTOP_CONFIG}" 2>/dev/null || true
                sed -i -E 's/"sentryToken"[[:space:]]*:[[:space:]]*"[^"]*"/"sentryToken":""/g' "${DESKTOP_CONFIG}" 2>/dev/null || true
            fi
            echo -e "${GREEN}  [v] Stripped org IDs and session auth links from config.json.${NC}"
        fi

        # 6. Sanitize plan usage & performance tracking
        if [[ "${ACTIVE_LANG}" == "ru" ]]; then
            echo -e "${CYAN}[5/6] Очистка истории использования тарифа и системных метрик...${NC}"
        else
            echo -e "${CYAN}[5/6] Sanitizing plan usage history & system metrics...${NC}"
        fi

        rm -f "${DESKTOP_PLAN_USAGE}" "${DESKTOP_PERF_DB}" "${DESKTOP_PERF_JOURNAL}" 2>/dev/null || true
        rm -rf "${DESKTOP_CRASHPAD}" "${DESKTOP_SENTRY_DIR}" "${DESKTOP_LOGS_DIR}" 2>/dev/null || true

        # 7. Session Preservation or Wipe
        if [[ "${ACTIVE_LANG}" == "ru" ]]; then
            echo -e "${CYAN}[6/6] Проверка сохранности файлов сессий и очистка логов...${NC}"
        else
            echo -e "${CYAN}[6/6] Verifying session preservation & clearing logs...${NC}"
        fi

        if [[ "${WIPE_SESSIONS}" == true ]]; then
            rm -rf "${DESKTOP_SESSIONS_DIR}" 2>/dev/null || true
            echo -e "${YELLOW}  [!] Factory reset: local sessions and chat turns wiped.${NC}"
        else
            if [[ -d "${DESKTOP_SESSIONS_DIR}" ]]; then
                local remaining_sess=$(find "${DESKTOP_SESSIONS_DIR}" -type f 2>/dev/null | wc -l || echo 0)
                if [[ "${ACTIVE_LANG}" == "ru" ]]; then
                    echo -e "${GREEN}  [v] СОХРАНЕНО: ${remaining_sess} файлов локальных сессий Claude Code не тронуты!${NC}"
                else
                    echo -e "${GREEN}  [v] PRESERVED: ${remaining_sess} local session files kept safe and untouched!${NC}"
                fi
            fi
        fi
    fi

    echo -e "\n${GREEN}======================================================================${NC}"
    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${GREEN}          СБРОС И ОЧИСТКА УСПЕШНО ЗАВЕРШЕНЫ!${NC}"
        echo -e "${WHITE}  Все метаданные, связывающие устройство с прежними учетками, сброшены.${NC}"
    else
        echo -e "${GREEN}     ANTI-BAN & TELEMETRY RESET COMPLETED SUCCESSFULLY!${NC}"
        echo -e "${WHITE}  All metadata linking this machine to previous accounts has been severed.${NC}"
    fi
    echo -e "${GREEN}======================================================================${NC}\n"

    if [[ "${AUTO_MODE}" == false ]]; then
        read -r -p "Press Enter to return to menu / Нажмите Enter..."
    fi
}

# --- Execution Entry Point ---
if [[ "${AUTO_MODE}" == true ]]; then
    perform_reset
    exit 0
fi

while true; do
    clear
    echo -e "${CYAN}======================================================================${NC}"
    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${YELLOW}       CLAUDE ANTI-BAN & СБРОС ИДЕНТИФИКАТОРОВ УСТРОЙСТВА${NC}"
        echo -e "${WHITE}    Сброс ID железа, глубокой телеметрии и защита от привязки аккаунтов${NC}"
    else
        echo -e "${YELLOW}           CLAUDE ANTI-BAN & DEVICE ID RESET UTILITY${NC}"
        echo -e "${WHITE}    Reset Hardware IDs, Deep Telemetry & Account Linkages${NC}"
    fi
    echo -e "${CYAN}======================================================================${NC}\n"

    if [[ "${ACTIVE_LANG}" == "ru" ]]; then
        echo -e "${WHITE}Выберите действие:${NC}"
        echo -e "  [${GREEN}1${NC}] 🚀 Безопасный Anti-Ban сброс (сброс ID железа и телеметрии, СЕССИИ СОХРАНЯЮТСЯ)"
        echo -e "  [${YELLOW}2${NC}] 🔍 Посмотреть текущие идентификаторы устройства"
        echo -e "  [${CYAN}3${NC}] 🛡️ Создать резервную копию сейчас"
        echo -e "  [${CYAN}4${NC}] 🔄 Восстановить из резервной копии"
        echo -e "  [${RED}5${NC}] ⚠️ Полный Factory Reset (сброс ID + удаление всех локальных сессий)"
        echo -e "  [${WHITE}L${NC}] 🌐 Switch Language / Сменить язык (EN / RU)"
        echo -e "  [${GRAY}0${NC}] ❌ Выход\n"
        read -r -p "Введите номер действия [1-5, L, 0]: " menu_choice
    else
        echo -e "${WHITE}Select an action:${NC}"
        echo -e "  [${GREEN}1${NC}] 🚀 Safe Anti-Ban Reset (Reset device IDs & deep telemetry, KEEP sessions)"
        echo -e "  [${YELLOW}2${NC}] 🔍 View Current Identifiers & Telemetry Status"
        echo -e "  [${CYAN}3${NC}] 🛡️ Create Safety Backup Now"
        echo -e "  [${CYAN}4${NC}] 🔄 Restore From Backup"
        echo -e "  [${RED}5${NC}] ⚠️ Full Factory Reset (Reset IDs + Wipe All Sessions)"
        echo -e "  [${WHITE}L${NC}] 🌐 Switch Language / Сменить язык (EN / RU)"
        echo -e "  [${GRAY}0${NC}] ❌ Exit\n"
        read -r -p "Enter option [1-5, L, 0]: " menu_choice
    fi

    case "${menu_choice}" in
        1)
            WIPE_SESSIONS=false
            perform_reset
            ;;
        2)
            view_identifiers
            ;;
        3)
            create_backup "manual"
            read -r -p "Press Enter to continue..."
            ;;
        4)
            restore_backup
            ;;
        5)
            echo ""
            if [[ "${ACTIVE_LANG}" == "ru" ]]; then
                echo -e "${RED}ВНИМАНИЕ: Будут удалены все локальные сессии Claude Code!${NC}"
                read -r -p "Для подтверждения полного сброса введите 'YES': " conf
            else
                echo -e "${RED}WARNING: All local Claude Code sessions and chat turns will be deleted!${NC}"
                read -r -p "Type 'YES' to confirm full factory reset: " conf
            fi
            if [[ "${conf}" == "YES" ]]; then
                WIPE_SESSIONS=true
                perform_reset
            else
                echo -e "${GRAY}Cancelled / Отменено.${NC}"
                sleep 1
            fi
            ;;
        l|L)
            if [[ "${ACTIVE_LANG}" == "ru" ]]; then
                ACTIVE_LANG="en"
            else
                ACTIVE_LANG="ru"
            fi
            echo "${ACTIVE_LANG}" > "${LANG_CONFIG_FILE}" 2>/dev/null || true
            ;;
        0|q|Q)
            echo "Exiting..."
            exit 0
            ;;
        *)
            ;;
    esac
done
