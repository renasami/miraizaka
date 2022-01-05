FROM python:3.9-buster

ENV DEBIAN_FRONTEND=noninteractive
ARG CUDA

COPY machine_learn/files/ tmp/files/
RUN set -x && \
	chmod 755 /tmp/files/install_*.sh && \
	/tmp/files/install_torch.sh && \
	/tmp/files/install_jupyter.sh && \
	rm -rf /tmp/files

VOLUME /app
WORKDIR /app

CMD ["jupyter", "lab", "--allow-root"]