"""Run MFA with the exact interpreter and DLL paths shipped with the app."""
if __name__ == "__main__":
    from runtime import configure_runtime
    configure_runtime()
    from montreal_forced_aligner.command_line.mfa import mfa_cli
    mfa_cli()
