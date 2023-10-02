function linkType = linktype_rmi_teamcenter
%
% This file explains how to implement a custom link type to support
% requirements linking between Simulink and a custom requirements
% management application.
% 
% Save this file with a modified name on your MATLAB path, provide string
% attributes and member functions as described below, and then register this
% new custom linktype with the following command:
% 
% >> rmi('register', 'linktype_fileame')
% 
% You must register a custom requirement link type before using it.
% Once registered, the link type will be reloaded in subsequent
% sessions until you unregister it.  
%
% Unregister like this:
% >> rmi('unregister', 'linktype_filename')
%

%  Copyright 2011-2017 The MathWorks, Inc.
%  

    % Create a default (blank) requirement link type 
    linkType = ReqMgr.LinkType;

    %%%%%%%%%%%%%%
    % ATTRIBUTES %
    %%%%%%%%%%%%%%
    
    % Registration attribute is the name of the file that creates the
    % object. Registration name is stored in the requirement link structure to
    % uniquely identify the link type.
    linkType.Registration = mfilename;

    % Label for this link type to be displayed in menus and dialogs
    linkType.Label = 'Teamcenter Item Revision';

    % Is there a physical file on the hard drive for each document of your
    % custom type? Set to 0 if No.
    linkType.IsFile = 0;  
    
    % If target documents are files, list possible extensions.
    % You may list more than one.
    % In the example below, the 'document' field in the requirement link
    % structure will expect strings like DOCNAME.ext1 or DOCNAME.ext2,
    % the Browse dialog will filter the file list accordingly.
    linkType.Extensions = {}; % = {'.ext1', '.ext2'}

    % Location delimiters.
    % Link target is identified by the document name and the location ID.
    % The first character in the .id field has the special purpose of
    % defining the type of identifier in the rest of the field. Your custom
    % document type may support the following location types:
    %
    %     ? - Search text located somewhere in the document
    %     @ - Named item such as a requirement object ID, etc.
    %     # - Page number or item number  
    %     > - Line number
    %     $ - Sheet range for a spreadsheet
    linkType.LocDelimiters = '#';
    
    % Version id for custom extensions, not currently used
    %linkType.Version = ''; 

    % For document types that support selection-based linking:
    %
    % Specify what label to display in context menus for the 
    % selection-based linking shortcut. Define only if 
    % your custom document type supports selection-based
    % linking. You will also need to define the SelectionLinkFcn 
    % method, see below.
    linkType.SelectionLinkLabel = 'Link to Teamcenter Item Revision...';

    %%%%%%%%%%%
    % METHODS %
    %%%%%%%%%%%
    
    % Implementation for NavigateFcn must be provided, see example below.
    linkType.NavigateFcn = @NavigateFcn;
    
    % All other member functions are optional. 
    % Uncomment and provide implementation as required.
    %
    linkType.ContentsFcn = @ContentsFcn;       % for document index
    %linkType.BrowseFcn = @BrowseFcn;           % choose a document
    %linkType.CreateURLFcn = @CreateURLFcn;     % for portable links
    %linkType.IsValidDocFcn = @IsValidDocFcn;   % for consistency checking
    %linkType.IsValidIdFcn = @IsValidIdFcn;     % for consistency checking
    %linkType.IsValidDescFcn = @IsValidDescFcn; % for consistency checking
    %linkType.DetailsFcn = @DetailsFcn;         % for detailed report
    linkType.SelectionLinkFcn = @SelectionLinkFcn; % for selection linking
    linkType.HtmlViewFcn = @HtmlViewFcn;   % HTML-formatted content for given item
    %linkType.SummaryFcn = @SummaryFcn; % Get the string summary (SLOWWWWW)

    %linkType.GetAttributeFcn = @GetAttributeFcn;   % returns item's attribute value  
    %linkType.TextViewFcn = @TextViewFcn  % plain text version of HtmlViewFcn
    %linkType.GetResultFcn = @GetResultFcn  % fetch external results

    %linkType.BeforeUpdateFcn = @BeforeUpdateFcn;
    
    linkType.BacklinkCheckFcn = @BacklinkCheckFcn;
    linkType.BacklinkInsertFcn = @BacklinkInsertFcn;
    linkType.BacklinkDeleteFcn = @BacklinkDeleteFcn;
    linkType.BacklinksCleanupFcn = @BacklinksCleanupFcn;
end


function [tf, linkTargetInfo] = BacklinkCheckFcn(mwSourceArtifact, mwItemId, reqDoc, reqId)
    disp([mfilename ': BacklinkCheckFcn']);    

    disp([mwSourceArtifact '\n' mwItemId '\n' reqDoc '\n' reqId]);
    
    tf = false;
    linkTargetInfo = 'foo';
    %[tf, linkTargetInfo] = rmidoors.checkIncomingLink(mwSourceArtifact, mwItemId, moduleId, reqId);
end

function [navcmd, dispstr] = BacklinkInsertFcn(reqDoc, reqId, mwSourceArtifact, mwItemId, mwDomain)
    disp([mfilename ': BacklinkInsertFcn']);    

    disp([mwSourceArtifact '\n' mwItemId '\n' reqDoc '\n' reqId '\n' mwDomain]);    

    bareObjNum = reqId; %rmidoors.getNumericStr(reqId, doorsModuleId);
    if isnumeric(mwSourceArtifact)
        % This is the legacy use case, when caller passed SL/SF handle.
        % We can save some time by avoiding all the logic in ELSE below.
        [navcmd, dispstr] = rmi.objinfo(mwSourceArtifact);
        labelStr = ['[Simulink reference: ' dispstr ']'];
    else
        isTextRange = [];
        if nargin == 3
            if isa(mwSourceArtifact, 'slreq.data.SourceItem')
                % Newer use case: caller passed an internal API object
                mwDomain = mwSourceArtifact.domain;
                [mwSourceArtifact, mwItemId] = slreq.utils.getExternalLinkArgs(mwSourceArtifact);
                isTextRange = mwSourceArtifact.isTextRange();
            elseif ischar(mwSourceArtifact)
                % the only supported use case for now is SL block path,
                % which should be handled correctly by same utility
                [mwSourceArtifact, mwItemId] = slreq.utils.getExternalLinkArgs(mwSourceArtifact);
                % TODO: here we rely on the older slreq.utils.getDomainLabel() utility, 
                % while BacklinkInsertFcn() in linktype_rmi_word/excel
                % relies on a more efficient (and limited) slreq.backlinks.getSrcDomainLabel
                % We may want to unify at some point in future.
                mwDomain = slreq.utils.getDomainLabel(mwSourceArtifact);
            else
                % should not happen
                error('unsupported usage of BacklinkInsertFcn() with 3rd arg of type %s', class(mwSourceArtifact));
            end
        else
            % Caller passed ready-to-use arguments for external link.
            % This use case is either Consistency Checking "Fix All" in
            % 5th check for MATLAB Function code range links, or this is
            % called by the new Backlinks management utility.
            if nargin < 5
                isTextRange = rmisl.isSidString(mwSourceArtifact);
                mwDomain = slreq.backlinks.getSrcDomainLabel(mwSourceArtifact);
            end
        end
        
        % at this point we should know how to generae the backlink for mwItemId
        try
            [navcmd, dispstr] = slreq.backlinks.getBacklinkAttributes(mwSourceArtifact, mwItemId, mwDomain, isTextRange);
        catch Mex
            throwAsCaller(Mex);  % throws error if mwDomain type not supported
        end
        
        if strcmp(mwDomain, 'linktype_rmi_matlab')
            labelStr = ['[MATLAB reference: ' dispstr ']'];
        else
            labelStr = ['[Simulink reference: ' dispstr ']'];
            % TODO:
            % consider using "Simulink Test Case:" for linktype_rmi_testmgr
            % consider using "Simulink Data Entry:" for linktype_rmi_data
        end
    end
    if ~isempty(navcmd)
        %create the link in Teamcenter
        pythonenv = pyenv();
        py.teamcenter.init_python(pythonenv.Home);
        tc_slreq = py.importlib.import_module('teamcenter.tc_slreq');
        tc_slreq.insert_backlinks(bareObjNum, mwSourceArtifact, labelStr, navcmd);
    end
end

function success = BacklinkDeleteFcn(reqDoc, reqId, mwSourceArtifact, mwItemId)
    disp([mfilename ': BacklinkDeleteFcn']);    

    disp([mwSourceArtifact '\n' mwItemId '\n' reqDoc '\n' reqId]);    
    
    if nargin < 4
        % if caller passed a SourceItem object
        [mwSourceArtifact, mwItemId] = slreq.utils.getExternalLinkArgs(mwSourceArtifact);
    end


    % first of all, make sure there IS a BACKLINK in Teamcenter
    %if rmidoors.checkIncomingLink(mwSourceArtifact, mwItemId, reqDoc, reqId)
       % yes, there is a link - remove it
        %doorsModuleId = strtok(reqDoc);
        %bareObjNum = rmidoors.getNumericStr(reqId, doorsModuleId);
        %rmidoors.removeLink(doorsModuleId, bareObjNum, mwSourceArtifact, mwItemId);
        disp([reqDoc " "  reqId " " mwSourceArtifact " " mwItemId])
        success = true;
    %else
    %    success = false;
    %end

end

function [countRemoved, countChecked] = BacklinksCleanupFcn(reqDoc, mwSourceArtifact, linksData, doSaveBeforeCleanup)
    disp([mfilename ': BacklinksCleanupFcn']);    

    disp([mwSourceArtifact '\n' reqDoc '\n' linksData '\n' doSaveBeforeCleanup]);    

    pythonenv = pyenv();
    py.teamcenter.init_python(pythonenv.Home);
    tc_slreq = py.importlib.import_module('teamcenter.tc_slreq');
	tc_slreq.backlinks_cleanup(mwSourceArtifact, reqDoc, linksData);
	
    countRemoved = 0;
    countChecked = 0;
end

%function callerObj = BeforeUpdateFcn(callerObj)
%    importOptions = callerObj.importOptions;
%    
%end

%% function NavigateFcn(DOCUMENT, LOCATION)
    % Open 'document' and highlight or zoom into 'location'
function NavigateFcn(document, location)
    disp([mfilename ': In <' document '> Navigating to <' location '>']);    

    pythonenv = pyenv();
    py.teamcenter.init_python(pythonenv.Home);
    tc_slreq = py.importlib.import_module('teamcenter.tc_slreq');

    if ~isempty(document) && isempty(location)
		tc_slreq.reset_connection();
	else
		% construct and open a URL
		url = char(tc_slreq.get_url(document, location));
		web(url);
	end
end

function [LABELS, DEPTHS, LOCATIONS] = ContentsFcn(DOCUMENT, OPTIONS) %#ok<*DEFNU>
    % Used to display the document index tab of Link Editor dialog.
    % You can select an entry in Document Index list to create a
    % link. Should return cell arrays of unique LOCATIONS IDs and text
    % LABELS in matching order. DEPTHS is the same length array of
    % integers to convey parent-child relationships between LABELS, fill
    % with zeros if all locations are same depth.
    
    disp([mfilename ': Importing contents of ' DOCUMENT]);
    
    pythonenv = pyenv();
    py.teamcenter.init_python(pythonenv.Home);
    tc_slreq = py.importlib.import_module('teamcenter.tc_slreq');
    RESULTUPLE = tc_slreq.get_contents(DOCUMENT);


    %LABELS = {['Dummy Header in' DOCUMENT] ; 'Dummy sub-header'};
    i=1;
    LABELS = {};
    for LABEL = RESULTUPLE{1,1}
        LABELS{i,1} = char(LABEL{1});
        i = i+1;
    end
    

    %DEPTHS = [0 ; 1];
    i=1;
    DEPTHS = zeros(double(py.len(RESULTUPLE{1,2})), 1);
    for DEPTH = RESULTUPLE{1,2}
        DEPTHS(i) = double(DEPTH{1});
        i = i+1;
    end


    %LOCATIONS = {'dummy_location_1' ; 'dummy_location_2'};
    i=1;
    LOCATIONS = {};
    for LOCATION = RESULTUPLE{1,3}
        LOCATIONS{i,1} = char(LOCATION{1});
        i = i+1;
    end

end

function DOCUMENT = BrowseFcn()
    % Allows users to select a DOCUMENT via Browse button of Link Editor
    % dialog. Not required when linkType.isFile is true; a standard file
    % chooser is used filtered based on linkType.Extensions.
    [filename, pathname] = uigetfile({...
        '.ext1', 'My Custom Doc sub-type1'; ...
        '.ext2', 'My Custom Doc sub-type2'}, ...
        'Pick a requirement file');
    DOCUMENT = fullfile(pathname, filename);
end

function URL = CreateURLFcn(DOCPATH, DOCURL, LOCATION)
    % Construct a URL to a LOCATION in corresponding document,
    % for example:
    if ~isempty(DOCURL)
        URL = [DOCURL '#' LOCATION(2:end)];
    else
        URL = ['file:///' DOCPATH '#' LOCATION(2:end)];
    end
end

function SUCCESS = IsValidDocFcn(DOCUMENT, REFPATH)
    % Used for requirements consistency checking.
    % Returns true if DOCUMENT can be located.
    % Returns false if DOCUMENT name is invalid or not found, for example:
    SUCCESS = exist(DOCUMENT, 'file') == 2 || ...
        exist(fullfile(REFPATH, DOCUMENT), 'file') == 2;
end

function SUCCESS = IsValidIdFcn(DOCUMENT, LOCATION)
    % Used for requirements consistency checking.
    % Returns true if LOCATION can be found in DOCUMENT.
    % Returns false if LOCATION is not found. 
    % Should generate an error if DOCUMENT not found or fails to open.
    SUCCESS = true;  % Provide implementation depending on document type.
end

function [ SUCCESS, DOC_DESCRIPTION ] = IsValidDescFcn(DOCUMENT, LOCATION, LINK_DESCRIPTION)
    % SUCCESS is true if LINK_DESCRIPTION is the string found at LOCATION
    % in DOCUMENT. 
    % DOC_DESCRIPTION is empty if true.
    % DOC_DESCRIPTION is the string found at the location if not SUCCESS.
    % Should generate an error if DOCUMENT is not found or if LOCATION is
    % not found in DOCUMENT.
    SUCCESS = true; % Provide implementation depending on document type.
end

function [ DEPTHS, ITEMS ] = DetailsFcn(DOCUMENT, LOCATION, LEVEL)
    % Return related contents from the DOCUMENT. For example, if
    % LOCATION points to a section header, this function should try to
    % return the entire header and body text of the subsection.
    % ITEMS is a cell array of formatted fragments (tables, paragraphs,
    % etc.)  DEPTHS is the corresponding numeric array that describes
    % hierarchical relationship among items.
    % LEVEL is meant for "details level", not currently used.
    % Invoked when generating report.
    ITEMS = {'DetailsFcn not implemented', 'Need to query the document'};
    DEPTHS = [0 1];
end

function REQ = SelectionLinkFcn(OBJECT, MAKE2WAY)
    % Returns the requirement info structure determined by the current
    % selection in currently open document of this custom type.
    % 'MAKE2WAY' is a Boolean argument to specify whether navigation
    % control back to OBJECT is inserted in document.

    prompt = 'Requirement Specification URL: ';
    name = 'Teamcenter';
    result = inputdlg(prompt, name, [1 100], {''});
    if isempty(result)
        error('Action canceled by user.');
    end
    url = strtrim(result{1});

    pythonenv = pyenv();
    py.teamcenter.init_python(pythonenv.Home);
    tc_slreq = py.importlib.import_module('teamcenter.tc_slreq');
    
    SPECINFO = tc_slreq.get_spec(url); 
    REQ = rmi('createempty');
    REQ.linked = true;
    REQ.doc = [ char(SPECINFO{2}) '_' char(SPECINFO{3}) ';' char(SPECINFO{4}) ];
    REQ.id = ['#' char(SPECINFO{2})];
    REQ.description = char(SPECINFO{5});
    REQ.reqsys = 'linktype_rmi_teamcenter';
    
    disp(['Created in Requirements Editor: ' REQ.doc]);

end

function summary = SummaryFcn(specId, requirementId)
    pythonenv = pyenv();
    py.teamcenter.init_python(pythonenv.Home);
    tc_slreq = py.importlib.import_module('teamcenter.tc_slreq');

    summary = char(tc_slreq.get_summary(specId, requirementId));
end

function HTML = HtmlViewFcn(DOC, LOCATION, OPT_DETAILS_LEVEL)
    % implementation depends on available HTML export feature of RM application
    % disp([mfilename ': Getting HTML Text of ' LOCATION ' within ' DOC]);
    
    pythonenv = pyenv();
    py.teamcenter.init_python(pythonenv.Home);
    tc_slreq = py.importlib.import_module('teamcenter.tc_slreq');

    py_html = tc_slreq.get_viewable_html(DOC,LOCATION);
    
    HTML = char(py_html);
end

function VALUE = GetAttributeFcn(DOC, LOCATION, ATTRIBUTENAME)
    % implementation depends on attribute query API of RM application
    VALUE = app.API.getAttribute(DOC, LOCATION, ATTRIBUTENAME);
end

function text = TextViewFcn(DOC, LOCATION)
    % this is a plain text version of HtmlViewFcn().
    % use it to simplify and/or speed-up content export

    pythonenv = pyenv();
    py.teamcenter.init_python(pythonenv.Home);
    tc_slreq = py.importlib.import_module('teamcenter.tc_slreq');
    text = char(tc_slreq.get_viewable_text(DOC,LOCATION));
end

function RESULT = GetResultFcn(LINK)
    % fetch external results to integrate with verification statuses
    % LINK is an slreq.Link object
    %   fetches artifact details using LINK.destination object
    % RESULT should be a MATLAB struct with the following fields:
    %   status (required)   -- value from slreq.verification.Status :
    %                           Pass, Fail, Stale, Unknown
    %   timestamp (optional) -- datetime value; skip field or mark NaT to
    %                           skip stale result detection
    %   info (optional)     -- info string to show as tooltip
    %   error (optional)    -- error string to show as tooltip; has
    %                           precedence over 'info' field value
    RESULT.status = slreq.verification.Status.Pass;
    RESULT.timestamp = datetime(now, 'ConvertFrom', 'datenum', 'TimeZone', 'Local');
end
