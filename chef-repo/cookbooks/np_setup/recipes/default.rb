# Cookbook Name:: np_setup
# Recipe:: default
#
# Copyright 2012, 
#
# All rights reserved - Do Not Redistribute

# Setup libshadow so that we can install passwords

ENV['RUBYOPT'] = "rubygems"

# do an apt update
execute "apt-update-periodic" do
    command "apt-get update"
    ignore_failure = true
    only_if do
        not(File.exists?('/var/lib/apt/periodic/update-success-stamp')) or 
        (File.mtime('/var/lib/apt/periodic/update-success-stamp') < (Time.now - 86400))
    end
end

package "make" do 
    action :install
end

package "git-core" do
    action :install
end

gem_package "ruby-shadow" do
    action :install
end

#install required system packages
#TODO:  Use more Chef-like methods for this
bash "install-system-packages" do
    code <<-EOH
    apt-get install -y python-setuptools libgdal-dev proj libspatialindex1 libspatialindex-dev python-pip zlibc python-virtualenv python-dev python-numpy python-matplotlib python-gdal python-scipy 
    ldconfig
    EOH
end
