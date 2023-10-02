warning('off','all');
rmi('unregister','linktype_rmi_teamcenter');
warning('on','all');
rmi('register','linktype_rmi_teamcenter');
rmipref('StoreDataExternally',true);
disp('Teamcenter Integration Initialized.')