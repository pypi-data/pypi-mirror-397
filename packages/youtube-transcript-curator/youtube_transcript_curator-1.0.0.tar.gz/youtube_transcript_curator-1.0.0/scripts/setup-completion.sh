#!/bin/bash

# Setup bash/zsh tab completion for YouTube Transcript Curator

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Setting up tab completion for 'ytc' command..."

# Detect shell
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_TYPE="zsh"
    COMPLETION_DIR="${ZDOTDIR:-$HOME}/.zsh/completions"
    RC_FILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_TYPE="bash"
    COMPLETION_DIR="/usr/local/etc/bash_completion.d"
    RC_FILE="$HOME/.bash_profile"
else
    echo "❌ Unsupported shell. Please use bash or zsh."
    exit 1
fi

echo "Detected shell: $SHELL_TYPE"

# Create completion script
COMPLETION_SCRIPT="/tmp/ytc_completion"

cat > "$COMPLETION_SCRIPT" << 'EOF'
# YouTube Transcript Curator - Tab Completion
# Place in ~/.zsh/completions/_ytc (zsh) or /usr/local/etc/bash_completion.d/ytc (bash)

if [[ -n "${ZSH_VERSION}" ]]; then
    # ZSH completion
    _ytc_completion() {
        local state line

        _arguments \
            '1: :->command' \
            '*: :->args'

        case "$state" in
            command)
                compadd fetch info list open search stats delete ai extract config history help
                ;;
            args)
                case "${words[2]}" in
                    list)
                        # Check if we're completing after option flags
                        if [[ "${words[-2]}" == "--type" ]]; then
                            compadd regular live rec reg ls recording
                        elif [[ "${words[-2]}" == "--sort" ]]; then
                            compadd date published title channel duration views
                        elif [[ "${words[-2]}" == "--format" ]]; then
                            compadd compact full ids json
                        else
                            compadd --format --type --channel --sort --reverse --limit --align --help
                        fi
                        ;;
                    info)
                        compadd --last --description --help
                        ;;
                    open)
                        if [[ "${words[-2]}" == "--length" ]]; then
                            compadd short medium long
                        else
                            compadd --meta --summary --length --code --finder --youtube --time --search --last --books --tools --key-points --help
                        fi
                        ;;
                    ai)
                        if [[ "${words[-2]}" == "--length" ]]; then
                            compadd short medium long
                        else
                            compadd --prompt --summarize --length --last --overwrite --help
                        fi
                        ;;
                    history)
                        if [[ "${words[-2]}" == "--action" ]]; then
                            compadd all fetch delete
                        else
                            compadd --action --limit --help
                        fi
                        ;;
                    search)
                        # Check if previous word is --context
                        if [[ "${words[-2]}" == "--context" ]]; then
                            compadd 0 1 2 3 5 10
                        else
                            compadd --context --count --json --help
                        fi
                        ;;
                    fetch)
                        compadd --overwrite --no-timestamps --output-dir --help
                        ;;
                    delete)
                        compadd --last --force --help
                        ;;
                    config)
                        compadd show get set edit path reset init where move --help
                        ;;
                    extract)
                        compadd --books --tools --key-points --last --overwrite --help
                        ;;
                esac
                ;;
        esac
    }

    compdef _ytc_completion ytc
else
    # BASH completion
    _ytc_completion() {
        local cur prev words cword
        COMPREPLY=()
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"

        if [[ ${COMP_CWORD} -eq 1 ]]; then
            # Complete commands
            COMPREPLY=( $(compgen -W "fetch info list open search stats delete ai extract config history help" -- "$cur") )
        else
            case "${COMP_WORDS[1]}" in
                list)
                    # Check if previous word is an option that needs values
                    if [[ "${prev}" == "--type" ]]; then
                        COMPREPLY=( $(compgen -W "regular live rec reg ls recording livestream livestream_recording" -- "$cur") )
                    elif [[ "${prev}" == "--sort" ]]; then
                        COMPREPLY=( $(compgen -W "date published title channel duration views" -- "$cur") )
                    elif [[ "${prev}" == "--format" ]]; then
                        COMPREPLY=( $(compgen -W "compact full ids json" -- "$cur") )
                    # Also check if --type appears anywhere in the command line (for mid-completion)
                    elif printf '%s\n' "${COMP_WORDS[@]}" | grep -q "^--type$"; then
                        # If we started typing something after --type
                        if [[ "${prev}" != "--type" && ! "$cur" =~ ^- ]]; then
                            COMPREPLY=( $(compgen -W "regular live rec reg ls recording livestream livestream_recording" -- "$cur") )
                        else
                            COMPREPLY=( $(compgen -W "--format --type --channel --sort --reverse --limit --align --help" -- "$cur") )
                        fi
                    else
                        COMPREPLY=( $(compgen -W "--format --type --channel --sort --reverse --limit --align --help" -- "$cur") )
                    fi
                    ;;
                info)
                    COMPREPLY=( $(compgen -W "--last --description --help" -- "$cur") )
                    ;;
                open)
                    if [[ "${prev}" == "--length" ]]; then
                        COMPREPLY=( $(compgen -W "short medium long" -- "$cur") )
                    else
                        COMPREPLY=( $(compgen -W "--meta --summary --length --code --finder --youtube --time --search --last --books --tools --key-points --help" -- "$cur") )
                    fi
                    ;;
                ai)
                    if [[ "${prev}" == "--length" ]]; then
                        COMPREPLY=( $(compgen -W "short medium long" -- "$cur") )
                    else
                        COMPREPLY=( $(compgen -W "--prompt --summarize --length --last --overwrite --help" -- "$cur") )
                    fi
                    ;;
                history)
                    if [[ "${prev}" == "--action" ]]; then
                        COMPREPLY=( $(compgen -W "all fetch delete" -- "$cur") )
                    else
                        COMPREPLY=( $(compgen -W "--action --limit --help" -- "$cur") )
                    fi
                    ;;
                search)
                    if [[ "${prev}" == "--context" ]]; then
                        COMPREPLY=( $(compgen -W "0 1 2 3 5 10" -- "$cur") )
                    else
                        COMPREPLY=( $(compgen -W "--context --count --json --help" -- "$cur") )
                    fi
                    ;;
                fetch)
                    COMPREPLY=( $(compgen -W "--overwrite --no-timestamps --output-dir --help" -- "$cur") )
                    ;;
                delete)
                    COMPREPLY=( $(compgen -W "--last --force --help" -- "$cur") )
                    ;;
                help)
                    COMPREPLY=( $(compgen -W "fetch info list open search stats delete ai extract config history" -- "$cur") )
                    ;;
                config)
                    COMPREPLY=( $(compgen -W "show get set edit path reset init where move --help" -- "$cur") )
                    ;;
                extract)
                    COMPREPLY=( $(compgen -W "--books --tools --key-points --last --overwrite --help" -- "$cur") )
                    ;;
            esac
        fi
        return 0
    }

    complete -F _ytc_completion ytc
fi
EOF

# Install completion
if [[ "$SHELL_TYPE" == "zsh" ]]; then
    mkdir -p "$COMPLETION_DIR"
    cp "$COMPLETION_SCRIPT" "$COMPLETION_DIR/_ytc"
    echo "✓ Completion installed to: $COMPLETION_DIR/_ytc"
    echo ""
    echo "To enable completion in current session:"
    echo "  source $RC_FILE"
else
    # For bash, try common locations
    if [[ -w "/usr/local/etc/bash_completion.d" ]]; then
        cp "$COMPLETION_SCRIPT" "/usr/local/etc/bash_completion.d/ytc"
        echo "✓ Completion installed to: /usr/local/etc/bash_completion.d/ytc"
    elif [[ -w "/etc/bash_completion.d" ]]; then
        sudo cp "$COMPLETION_SCRIPT" "/etc/bash_completion.d/ytc"
        echo "✓ Completion installed to: /etc/bash_completion.d/ytc"
    else
        # Fallback: add to .bash_profile
        mkdir -p "$HOME/.bash_completion.d"
        cp "$COMPLETION_SCRIPT" "$HOME/.bash_completion.d/ytc"

        if ! grep -q "bash_completion.d" "$RC_FILE" 2>/dev/null; then
            cat >> "$RC_FILE" << 'COMPLETION'

# YouTube Transcript Curator bash completion
if [[ -d "$HOME/.bash_completion.d" ]]; then
    for file in "$HOME/.bash_completion.d"/*; do
        source "$file"
    done
fi
COMPLETION
        fi

        echo "✓ Completion installed to: $HOME/.bash_completion.d/ytc"
        echo ""
        echo "Added completion loader to $RC_FILE"
    fi

    echo ""
    echo "To enable completion in current session:"
    echo "  source $RC_FILE"
fi

rm "$COMPLETION_SCRIPT"

echo ""
echo "✅ Tab completion setup complete!"
echo ""
echo "⚠️  IMPORTANT: Reload your shell for completions to take effect:"
if [[ "$SHELL_TYPE" == "zsh" ]]; then
    echo "  exec zsh"
    echo "  or"
    echo "  source ~/.zshrc"
else
    echo "  exec bash"
    echo "  or"
    echo "  source ~/.bash_profile"
fi
echo ""
echo "Try it out:"
echo "  ytc <TAB>        # Show available commands"
echo "  ytc list <TAB>   # Show options for list"
echo "  ytc list --ali<TAB>  # Completes to --align"
