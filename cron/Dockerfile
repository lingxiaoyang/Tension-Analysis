FROM alpine:3.10
COPY cronjob_remove_stale_files /etc/crontabs/root
CMD ["crond", "-f", "-d", "8"]
