FROM ruby:2.6.3-alpine

COPY . /app
RUN apk add --no-cache build-base sqlite-dev sqlite-libs && \
        cd /app && \
        bundle install && \
        apk del --purge build-base sqlite-dev

CMD cd /app && bundle exec puma -C puma.rb
