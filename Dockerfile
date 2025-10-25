FROM ubuntu:latest
LABEL authors="wsw"

ENTRYPOINT ["top", "-b"]