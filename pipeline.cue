// pipeline.cue
package job_applicator

import (
    "dagger.io/dagger"
    "universe.dagger.io/docker"
)

dagger.#Plan & {
    client: {
        filesystem: {
            "./src": read: contents: dagger.#FS
            "./data": read: contents: dagger.#FS
            "./config.json": read: contents: dagger.#File
            "./output": write: contents: dagger.#FS
        }
        env: {
            GEMINI_API_KEY: string
        }
    }

    actions: {
        // Base image with dependencies
        base: docker.#Build & {
            steps: [
                docker.#Pull & {
                    source: "python:3.10-slim"
                },
                docker.#Run & {
                    command: {
                        name: "apt-get"
                        args: ["update"]
                    }
                },
                docker.#Run & {
                    command: {
                        name: "apt-get"
                        args: ["install", "-y", "wget", "gnupg", "unzip"]
                    }
                },
                docker.#Run & {
                    command: {
                        name: "wget"
                        args: ["-q", "-O", "-", "https://dl-ssl.google.com/linux/linux_signing_key.pub"]
                    }
                },
                docker.#Run & {
                    command: {
                        name: "apt-key"
                        args: ["add", "-"]
                    }
                },
                docker.#Run & {
                    command: {
                        name: "sh"
                        args: ["-c", "echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google.list"]
                    }
                },
                docker.#Run & {
                    command: {
                        name: "apt-get"
                        args: ["update"]
                    }
                },
                docker.#Run & {
                    command: {
                        name: "apt-get"
                        args: ["install", "-y", "google-chrome-stable"]
                    }
                },
                docker.#Copy & {
                    contents: "selenium==4.10.0\nbeautifulsoup4==4.12.2\nwebdriver-manager==3.8.6\ngoogle-generativeai==0.3.1\npandas==2.0.3\nrequests==2.31.0"
                    dest: "/requirements.txt"
                },
                docker.#Run & {
                    command: {
                        name: "pip"
                        args: ["install", "--no-cache-dir", "-r", "/requirements.txt"]
                    }
                },
                docker.#Run & {
                    command: {
                        name: "mkdir"
                        args: ["-p", "/app/src", "/app/data", "/app/output"]
                    }
                }
            ]
        }

        // Job Applicator System
        jobApplicator: docker.#Build & {
            steps: [
                docker.#Copy & {
                    input: base.output
                    contents: client.filesystem."./src".read.contents
                    dest: "/app/src"
                },
                docker.#Copy & {
                    input: base.output
                    contents: client.filesystem."./data".read.contents
                    dest: "/app/data"
                },
                docker.#Copy & {
                    input: base.output
                    contents: client.filesystem."./config.json".read.contents
                    dest: "/app/config.json"
                },
                docker.#Set & {
                    config: {
                        env: {
                            GEMINI_API_KEY: client.env.GEMINI_API_KEY
                        }
                        entrypoint: ["python", "/app/src/job_applicator_agent/main.py", "/app/config.json"]
                    }
                }
            ]
        }

        // Run the job application system
        run: docker.#Run & {
            input: jobApplicator.output
            mounts: {
                "output": {
                    dest: "/app/output"
                    type: "volume"
                }
            }
            export: {
                directories: "/app/output": client.filesystem."./output".write.contents
            }
        }
    }
}