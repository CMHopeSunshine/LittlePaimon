FROM python:slim

RUN pip3 --no-cache-dir install nb-cli

ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

RUN ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN apt-get update && apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /data/pkg

COPY . .

RUN sed -i 's/^\-\-index\-url\s.*$//' requirements.txt && \
    pip3 install --no-cache-dir -r requirements.txt

RUN playwright install-deps && \
    playwright install chromium && \
    rm -rf /var/lib/apt/lists/*

CMD ["nb", "run"]