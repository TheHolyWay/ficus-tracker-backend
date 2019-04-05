#!/usr/bin/env bash

# Install helpful tools
echo "==> Install helpful tools"
yum install -y mc net-tools bind-utils epel-release nmap

# Configure mcedit
echo "==> Configure mcedit"
cp /usr/share/mc/syntax/sh.syntax /usr/share/mc/syntax/unknown.syntax

# Configure date/time
echo "==> Configure date/time"
mv /etc/localtime /etc/localtime.bak
ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime

# History configuratuin
echo "==> Configure history"
echo "# History configuratuin" >> ~/.bashrc
echo "export HISTSIZE=10000" >> ~/.bashrc
echo "export HISTTIMEFORMAT=\"%h %d %H:%M:%S \"" >> ~/.bashrc
echo "PROMPT_COMMAND='history -a'" >> ~/.bashrc
echo "export HISTIGNORE=\"ls:ll:history:w:htop\"" >> ~/.bashrc

source ~/.bashrc

# Install Python
echo "==> Install python"
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum install -y python36u python36u-devel python36u-pip
pip3.6 install --upgrade pip setuptools ipython

# Install Git
echo "==> Install git"
yum install -y curl-devel expat-devel gettext-devel openssl-devel zlib-devel git
git config --global user.name "mr. VladOS"
git config --global user.email vladislav.vlasov.dev@gmail.com
git config --global core.editor mcedit

# Install docker
echo "==> Install docker"
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce

echo "==> Set docker user"
usermod -aG docker $(whoami)

echo "==> Enable and start docker service"
systemctl enable docker.service
systemctl start docker.service

# Install docker compose
echo "==> Install docker-compose"
yum -y upgrade python*
pip3 install docker-compose
docker-compose version