import asyncio
import logging
import os

from daytona_sdk import (
    CodeLanguage,
    CreateSandboxFromImageParams,
    Daytona,
    DaytonaConfig,
    Resources,
    SessionExecuteRequest,
    VolumeMount,
)

logger = logging.getLogger(__name__)


async def daytona_run():
    daytona = Daytona(
        DaytonaConfig(
            api_key="dtn_277b52c5d3c7efaf40752743aa4dad5c3297697b86ae441b04d6ec24c8d1f2ef",
        )
    )
    volume = daytona.volume.get("my-volume", create=True)
    mount_dir_1 = "/home/daytona/workspace"
    sandbox = daytona.create(
        timeout=60 * 60 * 8,
        params=CreateSandboxFromImageParams(
            language=CodeLanguage.PYTHON,
            image="gitgit188/gomtm",
            auto_stop_interval=0,
            resources=Resources(
                cpu=2,
                memory=3,
                disk=1,
            ),
            volumes=[VolumeMount(volumeId=volume.id, mountPath=mount_dir_1)],
        ),
    )

    try:
        session_id = "exec-session-1"
        sandbox.process.create_session(session_id)

        command = sandbox.process.execute_session_command(
            session_id,
            SessionExecuteRequest(
                command="""cd ~ && sudo mkdir -p .vol \
&& sudo chmod -R 777 .vol \
&& sudo chown -R $(whoami) .vol \
&& sudo mkdir -p workspace \
&& sudo chmod -R 777 workspace \
&& sudo chown -R $(whoami) workspace \
&& sudo npm install -g gomtm-cli \
&& gomtm server --ts-name=dtn -s=box -s=sshd -s=vnc -s=devcontainer
""",
                runAsync=True,
            ),
        )
        log_file_path = f"./logs/dtn-session_{session_id}/cmd_{command.cmd_id}.log"
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        with open(log_file_path, "w") as log_file:

            def handle_chunk(chunk: str):
                #  remove null bytes
                clean_chunk = chunk.replace("\x00", "")
                #  write to file
                log_file.write(clean_chunk)
                log_file.flush()

            await sandbox.process.get_session_command_logs_async(
                session_id, str(command.cmd_id), handle_chunk
            )
    except Exception as e:
        logger.error(f"Error processing command logs: {e}")
    daytona.delete(sandbox)


if __name__ == "__main__":
    asyncio.run(daytona_run())
