FROM nginx:alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# SSL certificates
COPY ssl /etc/nginx/ssl

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
