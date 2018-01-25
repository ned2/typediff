/*
 *
 * Typediff: A tool for exploring types used in the processing of text
 * by DELPH-IN HPSG grammars
 *
 * Author: Ned Letcher
 * http://github.com/ned2/typediff
 *
 * This file represents my first attempt at a non-trivial web application. It is
 * an exemplar of what is often referred to as 'jQuery spaghetti' -- a complex
 * and highly coupled pile of event listeners and callbacks with state being
 * stored in the DOM. One day I'd like to re-implement it using
 * best-practices. For now, to anyone trying to make sense of any of this: 
 * I'm so sorry.
 */


var POSITEMS = Array();
var NEGITEMS = Array();
var ALLITEMS = [POSITEMS, NEGITEMS];
var POSCOUNTER = 0;
var NEGCOUNTER = 0;
var DESCENDANTS = {};
var POSPROFILES = Array();
var NEGPROFILES = Array();
var FADELENGTH = 400;
var ANNOTATION_MODE = false;
var ANNOTATION_LABEL = null;
var ANNOTATION_NAME = '';
var ANNOTATION_LABELS = [
    'that',
    'bare',
    'wh-simple',
    'wh-complex-1',
    'wh-complex-2',
    'wh-complex-3',
    'wh-complex-4',
    'wh-complex-5',
    'wh-complex-6',
    'wh-complex-7',
    'wh-complex-8',
    'integrated-non-inf',
    'integrated-inf',
    'supplementary',
    'cleft',
    'fused',
    'subject',
    'object',
    'predicative-comp',
    'comp-of-prep',
    'adjunct',
    'genitive-subj-det',
    'comp-of-aux-verb',
    'oblique-comp',
    'relative',
    'non-relative',
    'wh',             // broken
    'wh-complex',     // broken
    'integrated',     // broken
];

var BLACKLISTTYPES = Array();
var WHITELISTTYPES = Array();

// these should match the corresponding checkboxes in HTML
var LONGLABELS = false;
var SUPERS = false;

var COMPARE = _.difference;
var GROUP_OP = _.union;


function linkify(url, text, title) { 
    if (title === undefined) title = '';
    return '<a title="' + title + '" href="' + encodeURI(url) + '">' + text + '</a>';
}

function makeFangornQueryUrl(treebank, query) {
    return FANGORNPATH + '/search?corpus=' + treebank + '&query=' + query.toUpperCase(); 
}

function isERG(grammar) { return grammar.match('t?erg') !== null;}
function getItemId($item) { return parseInt($item.attr('id').split('-')[2]); }
function getItemType($item) { return $item.attr('id').split('-')[0]; }
function getItems(polarity) { return (polarity == 'pos') ? POSITEMS : NEGITEMS; }
function getItem($item) { return getItems(getItemType($item))[getItemId($item)]; }
function getDerivationId($deriv) { return parseInt($deriv.attr('id').split('-')[1]); }
function haveItems() { return POSITEMS.length > 0 || NEGITEMS.length > 0; }
function havePosItems() { return POSITEMS.length > 0; }
function haveNegItems() { return NEGITEMS.length > 0; }
function getItemObject($item){
    var id = getItemId($item);
    var polarity = getItemType($item);
    var items = getItems(polarity);
    return items[id];
}

function numActivePosItems(){
    return _.sumBy(POSITEMS, function(value){return !value.disabled | 0;});
}

function numActiveNegItems(){
    return _.sumBy(NEGITEMS, function(value){return !value.disabled | 0;});
}

function getDerivation($deriv) { 
    // given a derivation jQuery element, returns the corresponding derivation
    // data model object
    item = getItem($deriv.closest('.item'));
    return item.readings[getDerivationId($deriv)];
}

function pluralize(str, num) { return (num == 1) ? str : str + 's'; }
function incrCounter(type) { return (type == 'pos') ? POSCOUNTER++ : NEGCOUNTER++;}
function decrCounter(type) { return (type == 'pos') ? POSCOUNTER-- : NEGCOUNTER--;}

function toggleItemType($item) {
    var type = getItemType($item);
    var itemId = $item.attr('id'); 
    if (type == 'pos')
        $item.attr('id', itemId.replace('pos', 'neg')); 
    else
        $item.attr('id', itemId.replace('neg', 'pos')); 
}


function updateCompare(operator){
    $("#extra-group-operator .set-operator").removeClass('enabled');
    $("#extra-group-operator .set-operator[data-operator='"+operator+"']").addClass('enabled');

    if (operator == 'difference')
        COMPARE = _.difference;
    else if (operator == 'intersection') 
        COMPARE = _.intersection;
    else if (operator == 'union') 
        COMPARE = _.union;
}


function loadAnnotationMode(label){
    if (label == 'start'){
        ANNOTATION_LABEL = ANNOTATION_LABELS[0]; 
    } else {
        if (ANNOTATION_LABELS.indexOf(label) == -1)
            alert(`'${label}' is not a valid annotation label.`);
        else
            ANNOTATION_LABEL = label;
    }

    if (ANNOTATION_LABEL != null){
        ANNOTATION_MODE = true;
        $('#phenomenon-label').html(ANNOTATION_LABEL);
        $('#success-box').hide();
        $('#annotation-box').show();
        doDiff();
    }
}

//Submit button creates url with next label and loads it

function updateUrl() {
    var params = []; 

    var makeParam = function(param, value) {
        return [param, '=', value].join('');
    };

    var operator = $('#extra-group-operator .set-operator.enabled').data('operator');

    if (ANNOTATION_MODE) {
        params.push(makeParam('annotate', ANNOTATION_LABEL));
        params.push(makeParam('annotator', ANNOTATION_NAME));
    }
    
    params.push(makeParam('count', $('#count-input').val()));
    params.push(makeParam('treebank', $("#treebank-input").val()));
    params.push(makeParam('labels', $("input[name=labels]:checked").val()));
    params.push(makeParam('tagger', $("input[name=tagger]:checked").val()));
    params.push(makeParam('mode', operator));
    params.push(makeParam('supers', $("input[name=supers]").prop('checked')));
    params.push(makeParam('fragments', $("input[name=fragments]").prop('checked')));

    // extract the text of all POS and PEG items but exclude those that came
    // from a profile result as they must be restored separately
    var $posItems = $('#pos-items .item').not('.profile').find('.text'); 
    var $negItems = $('#neg-items .item').not('.profile').find('.text'); 

    if ($posItems.length > 0) {
        var Aitems = _.map($posItems, function (x) { return x.title; });
        params.push(makeParam('Agrammar', $('#pos-items .item').attr('grammar')));
        params.push(makeParam('A', Aitems.join('|||')));
    }

    if ($negItems.length > 0) {
        var Bitems = _.map($negItems, function (x) { return x.title; });
        params.push(makeParam('Bgrammar', $('#neg-items .item').attr('grammar')));
        params.push(makeParam('B', Bitems.join('|||')));
    }

    if (POSPROFILES.length > 0) {
        var value = POSPROFILES.join('|||').replace(/=/g, '+');
        params.push(makeParam('Aprofiles', value));
    }
    if (NEGPROFILES.length > 0) {
        var value = NEGPROFILES.join('|||').replace(/=/g, '+');
        params.push(makeParam('Bprofiles', value));
    }

    if (BLACKLISTTYPES.length > 0) {
        var value = BLACKLISTTYPES.join(',');
        params.push(makeParam('excludeTypes', value));
    }

    if (WHITELISTTYPES.length > 0) {
        var value = WHITELISTTYPES.join(',');
        params.push(makeParam('includeTypes', value));
    }

    window.location.hash = encodeURI(params.join('&'));
    updateButtons();
}


function loadUrlParams() {
    var hash = decodeURI(window.location.hash);
    var params = hash.replace(/^#/, '').split('&');

    if (params.length === 0 || params[0] === "")
        return;

    var Ainput = [];
    var Binput = [];
    var Agrammar = false;
    var Bgramamr = false;
    var annotationLabel = null;
    
    for (var i=0; i < params.length; i++) {
        var p = params[i];

        if (p == '')
            continue;

        var fields = p.split('=');
        var param = fields[0];
        var value = fields[1];

        if (param === '' || value === '')
            continue;

        if (param == 'count')
            $('#count-input').val(value);
        else if (param == 'labels') {
            $('input[value='+value+']').prop('checked', true);
            if (value == 'long')
                LONGLABELS = true;
            else
                LONGLABELS = false;
        } else if (param =='tagger') {
            $('input[value='+value+']').prop('checked', true);
        } else if (param == 'mode') {
            updateCompare(value);
        } else if (param == 'treebank') {
            $('#treebank-input').val(value);
        } else if (param == 'supers') {
            var val = JSON.parse(value);
            SUPERS = val;
            $('input[name=supers]').prop('checked', val);
        } else if (param == 'fragments') {
            var val = JSON.parse(value);
            $('input[name=fragments]').prop('checked', val);
        } else if (param == 'Agrammar') {
            var Agrammar = value;
            $('#grammar-input').val(value);
        } else if (param == 'Bgrammar') {
            var Bgrammar = value;
            var currGram = $('#grammar-input').val();
            if (currGram != null)
                $('#grammar-input').val(value);
        } else if (param == 'A') {
            var Ainput = value.split('|||');
        } else if (param == 'B') {
            var Binput = value.split('|||');
        } else if (param == 'Aprofiles'){
            var posProfiles = value.split('|||');
        } else if (param == 'Bprofiles'){
            var negProfiles = value.split('|||');
        } else if (param == 'excludeTypes') {
            BLACKLISTTYPES = value.split(',');
        } else if (param == 'includeTypes') {
            WHITELISTTYPES = value.split(',');
        } else if (param == 'annotate') {
            annotationLabel = value;
        } else if (param == 'annotator') {
            $('#annotation-name').val(value);
        }

    }

    if (posProfiles != null ) {
        for (var i=0; i < posProfiles.length; i++) { 
            var values = posProfiles[i].replace(/\+/g, '=').split(':');
            var prof = values[0];
            var filter = values[1];
            processProfiles({
                posProfile: prof,
                posFilter: filter,
                negProfile: null,
                negFilter: ''
            });
        }
    }

    if (negProfiles != null ) {
        for (var i=0; i < negProfiles.length; i++) { 
            var values = negProfiles[i].split(':');
            var prof = values[0];
            var filter = values[1];
            processProfiles({
                posProfile: null,
                posFilter: '',
                negProfile: prof,
                negFilter: filter
            });
        }
    }

    if (!(Agrammar || Bgrammar)) {
        return;
    }

    // the typediff queries only work for one grammar at a time, so if
    // the A grammar and B grammar are different, we need to do first
    // one then the other.
    if (!Agrammar){
        // no A items, just do B items
        $('#grammar-input').val(Bgrammar);
        $('#neg-input').val(Binput.join('\n'));
        processItems();
    } else if (!Bgrammar){
        // no B items, just do A items
        $('#grammar-input').val(Agrammar);
        $('#pos-input').val(Ainput.join('\n'));
        processItems();
    } else if (Agrammar == Bgrammar) {
        // both A and B items using the same grammar
        $('#grammar-input').val(Agrammar);
        $('#pos-input').val(Ainput.join('\n'));
        $('#neg-input').val(Binput.join('\n'));
        processItems();
    } else {
        // both A and B items but using different grammars
        // process A items then process B items with a callback
        $('#grammar-input').val(Agrammar);
        $('#pos-input').val(Ainput.join('\n'));
        processItems(function() {
            $('#grammar-input').val(Bgrammar);
            $('#neg-input').val(Binput.join('\n'));
            processItems();
        });
    }

    if (annotationLabel) {
        loadAnnotationMode(value);
    }
}


function processItems(callback) {
    showStatusBox('#waiting-box');
    var grammar =  $('#grammar-input').val();
    var data = {
        'pos-items' : $('#pos-input').val(), 
        'neg-items' : $('#neg-input').val(),
        'grammar-name' : grammar,
        'count' : $('#count-input').val(),
        'load-descendants': !Boolean(DESCENDANTS[grammar]),
        'supers': $('input[name=supers]').prop('checked'),
        'tagger': $("input[name=tagger]:checked").val(),
        'fragments': $('input[name=fragments]').prop('checked')
    };  
    var posting = $.post('/parse-types', data);
    posting.done(processPostData, function(data){
        if (data.success && callback)
            callback();
    });
}


function processProfiles(savedProfiles) {
    showStatusBox('#waiting-box');
    if (savedProfiles != null){
        var posProfile = savedProfiles.posProfile;
        var negProfile = savedProfiles.negProfile;
        var posFilter = savedProfiles.posFilter;
        var negFilter = savedProfiles.negFilter;
    } else {
        var posProfile = $('#pos-profile-input').val();
        var negProfile = $('#neg-profile-input').val();
        var posFilter = $('#pos-profile-filter').val();
        var negFilter = $('#neg-profile-filter').val();
    }

    // we're assuming that POS and NEG profiles used the same grammar
    var grammar =  PROFILES[(posProfile||negProfile)].grammar;

    var data = {
        'pos-profile': posProfile,
        'neg-profile': negProfile,
        'pos-profile-filter': posFilter, 
        'neg-profile-filter': negFilter,
        'load-descendants': !Boolean(DESCENDANTS[grammar]) 
    };

    var posting = $.post('/process-profiles', data);

    posting.done(function(data){

        if (posProfile)
            POSPROFILES.push(`${posProfile}:${posFilter}`);
        if (negProfile)
            NEGPROFILES.push(`${negProfile}:${negFilter}`);

        if (posProfile || negProfile){
            $('#grammar-input').val(data.grammar);
            $('#treebank-input').val(data.treebank);
        }
            
    }, processPostData);
}


function processPostData(data) {
    // handles results of both /parse-types and /process-profiles

    if (data.success) {
        if (data.descendants) DESCENDANTS[data.grammar] = data.descendants;
        
        TYPEDATA = data.typeData;
        processItemResults(data['pos-items'], 'pos');
        processItemResults(data['neg-items'], 'neg');
        $('#pos-input, #neg-input').val('');
        //$('#pos-profile-input, #neg-profile-input').val(null);
        //$('#pos-profile-filter, #neg-profile-filter').val('');
        setOperator();
        // applyFilters calls doDiff even when there are no filters();
        applyFilters();
    } else {
        showStatusBox('#fail-box').html(data.error.replace(/\n/g, '<br/>'));
        updateButtons();
    }
}


function setOperator(){
    // if both, set to set difference; show options
    // otherwise, set to union; hide options
    if (POSITEMS.length && NEGITEMS.length) {
        updateCompare("difference");
        $("#extra-group-operator").show();
    } else {
        updateCompare("union");
        $("#extra-group-operator").hide();
    }
}


function processItemResults(newItems, type) {
    var template = $("#item-template").html();
    var items = getItems(type);

    for (var i = 0; i < newItems.length; i++) {
        var item = newItems[i];
        var $item = $(template).attr('grammar', item.grammar);
        if (item.type == "profile")
            $item.addClass('profile');
        var readings = item.readings.length;
        var counter = incrCounter(type);
        var id = type+'-item-'+counter;
        var $itemSection = $(['#',type,'-items'].join(''));

        items.push(item);
        $item.find('.hidden').hide();
        $item.find('.text').text(item.input).attr('title', item.input);
        $item.find('.number').text(counter+1);
        updateTreeCounts($item, readings);
        $item.attr('id', id);
        $itemSection.show();
        $itemSection.find('.item-list').append($item);

        var $treeBox = $item.find('.tree-box');

        for (var j=0; j < readings; j++) {
            var derivation = item.readings[j];
            var $derivation = $('<div>', {'class' : 'derivation', 
                                          'id' : 'derivation-'+j});
            if (j == 0) {
                derivation.active = true;
                $derivation.addClass('active');
            } else {
                derivation.active = false;
            }

            $treeBox.append($derivation);
        }

        // default is to use the best parse
        setItemHandlers($item);
    }
}


function showStatusBox(id) {
    $('#success-box, #waiting-box, #fail-box').hide();

    if (!(ANNOTATION_MODE && id == '#success-box'))
        $(id).show();
}
 

function updateButtons() {
    if (window.location.hash == '')
        $('#clear-button').addClass('disabled');
    else
        $('#clear-button').removeClass('disabled');        
    
    if (!haveItems()) {
        $('#swap-items-button').addClass('disabled');
    } else if (!(havePosItems() && haveNegItems())) {
        $('#swap-items-button').addClass('disabled');
        $('#clear-button').removeClass('disabled');
    } else {
        $('#swap-items-button').removeClass('disabled');
    }
}

function convertToPercentage(number, denominator, percent) {
    var float = number*100/denominator;
    var string = float.toFixed(2).toString();

    // make sure zero padded if need be
    if (string.length == 4)
        string = '0' + string;

    if (percent)
        string = string + "%";
    
    return string;
}


function makeTable(types, supers, itemCounts, grammar, typesToSupers, treebank) {
    /* create a new table with output types */
    var $table = $('<table>', {
        id: 'type-table',
        style: 'clear:none'
    }).html('<thead><tr><th></th><th>Kind</th><th>TF-IDF</th><th>A Items Coverage (%)</th><th>Treebank Coverage (%)</th><th>Type</th></tr></thead><tfoot><tr><th></th><th><select class="filter"><option selected value="(sign|synsem|head|cat|relation|predsort)">All</option></select></th><th></th><th></th><th></th><th></th></tr></tfoot>');
    var tbody = $('<tbody>').appendTo($table);
    
    function makeNode(type, kind, superOf) {
        var treebankPercentage = '';
        var tfIdfVal = '';
        
        if (treebank.data && !superOf) {
            var typeStats = treebank.data[type];
            var trees = (typeStats != undefined) ? typeStats.items : 0;
            treebankPercentage = convertToPercentage(trees, treebank.trees); 
            var tf = itemCounts[type];
            var idf =  Math.log(treebank.trees/(1+trees));
            var idfx =  1/(1+Math.log(1+trees));
            tfIdfVal = (tf*idf).toFixed(2);
            //tfIdfVal = (itemCounts[type]/(1+Math.log(trees))).toFixed(4);
        }
            
        // Make all the cells of the line 
        var rowNumber = $('<td>', {class : 'row-number'});        

        var typeKind = $('<td>', {
            text: kind,
            "data-order" : TYPEDATA[kind].rank
        });

        var itemCount = $('<td>', {
            class: 'items-stat', 
            text: convertToPercentage(itemCounts[type], numActivePosItems()),
            title: 'percentage of active A items found in'
        });

        var treebankCount = $('<td>', {
            class: 'items-stat', 
            text: treebankPercentage,
            title: 'percent of trees in treebank this type is found in'
        });

        var tfIdf = $('<td>', {
            class: 'items-stat', 
            text: tfIdfVal,
            title: 'TF-IDF'
        });

        var typeName = $('<td>', {
            'html' : `<div class="type-name">${type}</div>`,
            'class': kind + ' type',
            'title': `${type} (${kind} type)`,
            'style': 'background: ' + TYPEDATA[kind].col
        });

        if (ANNOTATION_MODE) {
            typeName.append('<div class="nec-ann type-button"><i class="fa fa-file-text" title="Annotate this item as necessary for the phenomenon"></i></div>');
            typeName.append('<div class="rel-ann type-button"><i class="fa fa-file-text-o" title="Annotate this item as relevant to the phenomenon"></i></div>');
        }
        
        typeName.append('<div class="filter-type-in type-button"><i class="fa fa-filter" title="limit items to those having this type" style="color:#d6caca"></i></div>');
        typeName.append('<div class="filter-type-out type-button"><i class="fa fa-filter" title="remove items that have this type"></i></div>');

        var typeLine = $('<tr>', {'class' : 'type-line'});

        if (superOf) {
            typeLine.addClass('super');
            typeName.addClass('super');
            typeName.attr('title', 'supertype of ' + superOf);
            itemCount.html('');
            treebankCount.html('');
            tfIdf.html('');
        }

        typeLine.append([
            rowNumber,
            typeKind,
            tfIdf,
            itemCount,
            treebankCount,
            typeName,
        ]);

        return typeLine;
    };

    // Actually make the types...

    for (var i=0; i < types.length; i++) {
        var type = types[i];
        var kind = DESCENDANTS[grammar][type] || "other";
        tbody.append(makeNode(type, kind, false));    

        if (typesToSupers && typesToSupers[type]) {
            var supers = typesToSupers[type];
            var sortedSupers = _.sortBy(supers, function(x) {return -x[1];});
            for (var k=0; k < supers.length; k++) {
                tbody.append(makeNode(sortedSupers[k][0], kind, type));
            }
        }
    }

    var dt = $table.DataTable({
        dom: 'fit',
        paging: false,
        order: [[2, 'desc']],
        fixedHeader: true,
        columnDefs: [ {
            searchable: false,
            orderable: false,
            targets: 0
        } ],
        aoSearchCols: [
            null, 
            {
                sSearch: "(sign|synsem|head|cat|relation|predsort)",
                "bRegex": true
            },
            null, null, null, null
        ],
        initComplete: function () {
            // generate select options from unique values from columns
            // with select filters
            this.api().columns().every( function () {
                var column = this;
                var select = $('select.filter', column.footer());
                if (select.length != 0){
                    var order = function (x,y){
                        order = [
                            'sign', 'synsem', 'head', 'cat', 'relation',
                            'predsort','other'
                        ];
                        if (x == y)
                            return 0;
                        if (order.indexOf(x) < order.indexOf(y))
                            return -1;
                        return 1;
                    };
                    column.data().unique().sort(order).each(function (d, j) {
                        select.append('<option value="'+d+'">'+d+'</option>');
                    });
                    select.append('<option value=".*">All + other</option>');
                }
            });
        }
    });

    dt.columns().every(function(){
        var column = this;
        $('select.filter', this.footer()).on('change', function () {
            var val = this.value;
            var searchString = '^'+val+'$';
            var regex = true;
            column.search(searchString, regex, !regex, true).draw();
        });
    });

    dt.on( 'order.dt search.dt', function() {
        dt.column(0, {search:'applied', order:'applied'}).nodes().each(function (cell, i) {
            cell.innerHTML = (i+1)+'.';
        });
    }).draw();
    
    //return $table;
    // weird hack because datatables is not creating the container
    return $(dt.table().container()).append($table);

}

function addNecAnnotation(typeName) {
    addAnnotation(typeName, '#necessary-types');
}


function addRelAnnotation(typeName) {
    addAnnotation(typeName, '#relevant-types');
}

    
function addAnnotation(typeName, containerId){
    if (getAllAnnotations().indexOf(typeName) > -1) {
        alert(`You have already annotated ${typeName}`);
        return;
    }
        
    var grammar = $('#grammar-input').val();
    var kind = DESCENDANTS[grammar][typeName] || "other";
    var $ann = $('<div>', {
        'html' : typeName,
        'class' : kind + ' type',
        'title' : `${typeName} (${kind} type)`,
        'style' : 'background: ' + TYPEDATA[kind].col
    });
   
    $ann.append('<i title="remove this annotation" class="type-button del fa fa-times"></i>');
    $(containerId).append($('<div class="type-wrapper">').append($ann));

    $('#annotated-types-container .type .del').click(function(event) {
        event.stopPropagation();
        $(this).parent().remove();
    });
}


function getNecAnnotations() {
    return $('#necessary-types .type').map(
        function() {return $(this).text();}
    ).get();
}


function getRelAnnotations() {
    return $('#relevant-types .type').map(
        function() {return $(this).text();}
    ).get();
}


function getAllAnnotations() {
    var relAnns = getRelAnnotations();
    var necAnns = getNecAnnotations();
    return necAnns.concat(relAnns);
}


function makeFilterLists(grammar) {
    var makeFilterList = function (filters, id, text) {
        var typeFilters = Array();
        for (var i=0; i < filters.length; i++) {
            var typeName = filters[i];
            var kind = DESCENDANTS[grammar][typeName] || "other";
            var $filter = $('<div>', {
                'html' : typeName,
                'class' : kind + ' type',
                'title' : `${typeName} (${kind} type)`,
                'style' : 'background: ' + TYPEDATA[kind].col
            });
            $filter.append('<i title="remove this filter" class="type-button del fa fa-times"></i>');
            typeFilters.push($('<div class="type-wrapper">').append($filter));
        }

        var header = $('<div>', {
            text: text,
            class: 'type-list-header'
        });
        return $('<div>', {id: id, class: 'type-list'})
            .append(header)
            .append(typeFilters);
    };
    
    return $('<div>', {
        class: 'type-list-container'
    }).append([
        makeFilterList(BLACKLISTTYPES, 'black-filter-list', 'Excluded Types'),
        makeFilterList(WHITELISTTYPES, 'white-filter-list', 'Included Types'),
    ]);
}


function postDiff(types, supers, itemCounts, grammar, typesToSupers, treebank) {
    var outputPane = $('#output-pane-contents').empty(); 

    if (BLACKLISTTYPES.length > 0 || WHITELISTTYPES.length > 0) {
        var $filterList = makeFilterLists(grammar);
        var clearFilters = $('<div>', {class: "center"})
                .append($('<input>', {
                    id: "clear-filters",
                    type: "submit",
                    value: "Clear All",
                    title: "Clear all active filters"
                }));
        outputPane.append([$filterList, clearFilters]);
    }
    
    var $table = makeTable(types, supers, itemCounts, grammar, typesToSupers,
                           treebank);
    outputPane.append($table);
   
    // Do various status things...
    
    var addGrammarStatus = function(grammars, $status) {
        if (grammars.length > 0) {
            var first = grammars[0];
            if (_.every(grammars, function(x) { return x == first; })) {
                $status.removeClass('error').text(first);
            } else {
                var error_str = _.uniq(grammars).join(' and ') + '!';
                $status.addClass('error').text(error_str);
            }
            $status.prev().show();
            $status.show();
        } else {
            $status.prev().hide();
            $status.hide();
        }
    };

    $('#num-pos-items').text(POSITEMS.length);
    $('#num-neg-items').text(NEGITEMS.length);
    
    var posGrammars = _.map($('#pos-items .item'), function(x) { 
        return $(x).attr('grammar'); });
    var negGrammars = _.map($('#neg-items .item'), function(x) { 
        return $(x).attr('grammar'); });

    addGrammarStatus(posGrammars, $('#pos-grammar'));
    addGrammarStatus(negGrammars, $('#neg-grammar'));

    $('#numtypes').text(types.length);

    if (SUPERS)
        $('#numsupers').text(supers.length);
    else
        $('#numsupers').text('?');

    if (treebank)
        $('#treebank-details').html(treebank.name+'<br>'+treebank.trees+' trees');
    else
        $('#treebank-details').html('none');

    setTypeHandlers();
    updateUrl();
    showStatusBox('#success-box');
}


function updateActiveItems() {
    var numPos = numActivePosItems();
    var numNeg = numActiveNegItems();
    $('#pos-active-count').html(`<span>${numPos} ${pluralize('item', numPos)}</span>`);
    $('#neg-active-count').html(`<span>${numNeg} ${pluralize('item', numNeg)}</span>`);
}


function doDiff() {
    updateActiveItems();

    if (!haveItems()) return;
   
    $('.locked').each(function(index, elem) {
        elem.classList.remove('locked');
    });

    // We need to know which grammar we're working with in order to
    // get the correct list of descendants of 'sign' and 'synsem'
    // types etc as well as which supertypes come above which types in
    // the hierarchy.  For this we always use the POS grammar,
    // even for intersection and union mode as untangling which
    // grammars the types come from in the output is  not
    // worth the effort.
    var grammar = $('.item').attr('grammar');

    function getTypes(item) { 
        // get the types from all active readings in an item

        if (item.disabled) {
            return [];
        } else {
            return _.concat.apply([], _.map(item.readings, function(x) {
                return x.active ? Object.keys(x.types) : []; 
            }));
        }
    }

    function getSupers(item) { 
        // get the types from all active readings in an item
        if (item.disabled) {
            return [];
        } else {
            return _.concat.apply([], _.map(item.readings, function(x) {
                return x.active ? x.supers : []; 
            }));
        }
    }
    
    var posTypes = _.uniq(_.union.apply([], _.map(POSITEMS, getTypes))); 
    var posSupers = _.uniq(_.union.apply([], _.map(POSITEMS, getSupers))); 
    var negTypes = _.uniq(_.union.apply([], _.map(NEGITEMS, getTypes))); 
    var negSupers = _.uniq(_.union.apply([], _.map(NEGITEMS, getSupers))); 

    // algorithm for typeCounts:
    // uniq on each element in list
    // flatten the lists
    // countBy type names

    var itemCounts = _.countBy([].concat.apply([], _.map(_.map(POSITEMS, getTypes), _.uniq)));
    var types = COMPARE(posTypes, negTypes);
    var supers = COMPARE(posSupers, negSupers);
    
    var requests = [];
    var typesToSupers = false;
    var treebank = false;

    if (SUPERS && supers.length != 0) {
        // We need to lookup which types the supers are supertypes of.
        data = {
            'grammar-name' : grammar,
            'types'        : JSON.stringify(types),
            'supers'       : JSON.stringify(supers)
        };
        requests.push($.post('/find-supers', data));
    }

    var treebankAlias = $('select[name=treebank-name]').val();
    if (treebankAlias != 'none') {
        treebank = TREEBANKS[treebankAlias];

        // check to see if the treebank has already been loaded
        // before making a request to fetch it
        if (treebank.data == undefined)
            requests.push($.getJSON('/json/' + treebank.json));
    }

    // process the array of requests
    $.when.apply(null, function (){return requests;}()).done(function(results) {
        // ugh....
        function doThings(result) {
            if (result.typesToSupers != undefined)
                typesToSupers = result.typesToSupers;
            else
                treebank.data = result;
        }

        if (requests.length == 1) {
            doThings(results);
        } else {
            for (var i=0; i < arguments.length; i++)
                doThings(arguments[i][0]);
        }

        // All requests are done and processed, so do remaining things
        postDiff(types, supers, itemCounts, grammar, typesToSupers, treebank);
    });
}


function drawTrees($item) {
    var item = getItem($item);

    // Note that we have to make the derivation visible in case it was
    // previously hidden, otherwise the dimensions of the created SVG
    // won't be calculated correctly.
    for (var i=0; i < item.readings.length; i++) {
        var $svg = $(svgelement('svg')).attr('version', '1.1');
        var $derivation = $item.find('#derivation-'+i).append($svg);
        var wasHidden = $derivation.is(':hidden');
        $derivation.show();

        var g = render_tree($svg[0], item.input, item.readings[i].tree, LONGLABELS);
        var $g = $(g);

        // make an SVG element with the tree number
        var gnum = svgelement('g');
        var text = svgelement('text');
        var starty = $g.children().first().attr('y');
        $g.attr('transform', 'translate(0,'+starty+')');
        text.setAttributeNS(null, "x", 0);
        text.setAttributeNS(null, "y", starty);
        text.appendChild(document.createTextNode((i+1) + '.'));
        gnum.appendChild(text);

        // add the tree number and then the tree to the SVG
        $svg.append(gnum);
        $svg.append(g);

        // update the SVG element dimensions with the dimensions
        // calculated from the the child elements
        var bbox = g.getBBox();
        $svg.height(bbox.height + parseInt(starty));
        $svg.width(bbox.width);

        if (wasHidden)
            $derivation.hide();
    }
}


function removeSubTrees(trees) {
    if (trees.length < 2) 
        return;

    var treeSubsumes = function(t1, t2) { 
        return t2.from >= t1.from && t2.to <= t1.to; 
    };

    for (var i=1; i < trees.length; i++) {
        if (treeSubsumes(trees[i], trees[i-1])) {
            trees.splice(--i, 1);
        } else if (treeSubsumes(trees[i-1], trees[i])) {
            trees.splice(i, 1);
        }
    }
}


function resetSpans() {
    $('.item .text').each(function(index, elem) {    
        $this = $(this);
        $this.closest('.item').css({'background-color': 'white'});
        $this.html(this.title);
    });
}


/* Search a tree for all subtrees whose node is of type value and
 * return the list of subtrees. 
*/
function findTree(value, tree) {
    var stack = [tree];
    var found = [];
    while (stack.length > 0) {
        var t = stack.pop();
        if (t.rule == value || t.label == value) 
            found.push(t);
        for(var x in t.daughters) 
            stack.push(t.daughters[x]);
    }
    return found.reverse();
}


function highlightSpans(type) {
    $('.item').each(function(index, elem) {
        $item = $(elem);

        // span highlighting is based on the first active derivation.
        $derivation = $item.find('.derivation.active').first();
        var derivation = getDerivation($derivation);
        var trees = findTree(type, derivation.tree);

        // We only want to highlight the highest node of this type
        // Otherwise funky things will start happening when
        // we go to construct the highlighted text. So we go 
        // through the list of matched trees from this derivation, and
        // if any subsumes any other one, we remove the lower node.
        removeSubTrees(trees);

        if (!trees.length) 
            return;

        var $text = $item.find('.text');
        var text = $text.attr('title');
        var prev = 0;
        var parts = [];

        for (var i=0; i < trees.length; i++) {
            var tree = trees[i];
            var left = text.slice(prev, (!tree.from ? 0 : tree.from));
            var curr = text.slice(tree.from, tree.to);
            parts.push(left);
            parts.push('<span class="active">' + curr + '</span>');
            prev = tree.to + 1;
        }

        var end = text.slice(prev - 1, text.length);

        if ($item.attr('grammar') == 'jacy')
            var spacer = '';
        else
            var spacer = ' ';

        if (end.length > 1)
            end = spacer + end;

        $text.html(parts.join(spacer) + end);
    });
}


function updateTreeCounts($item, count) {
    var string = count + pluralize(' tree', count);
    $item.find('.tree-count').html(string);
}


function toggleTrees() {
    var types = _.map($('.type.active'), function (x) {
        // this assumes that there is no other inner text within the
        // typename <td> other than the text of the type-name.
        return x.innerText;
    });
    $('.derivation').each(function(index, elem) {
        var $derivation = $(elem);
        var derivation = getDerivation($derivation);
        var found = true;
        for (var i=0; i < types.length; i++) {
            var type = types[i]; 
            if (!_.has(derivation.types, type)) {
                found = false;
                $derivation.hide();
                break;
            }
        }
        if (found)
            $derivation.show();
    });

    $('.item').each(function(index, elem){
        var $item = $(elem); 
        var numActive = $item.find('.derivation').filter(function() {
            return $(this).css('display') !== 'none';
        }).size();

        updateTreeCounts($item, numActive);
    });
}


function isElementInViewport (el) {
    // Taken from http://stackoverflow.com/a/7557433
    // but with the boundary tests changed to capture elements that
    // continue over the edge of the viewport.
    
    if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();

    // element is not actually visible
    if (rect.bottom == 0 && rect.right == 0 && rect.top == 0 && rect.left == 0)
        return false;

    var height = (window.innerHeight || document.documentElement.clientHeight);
    var width = (window.innerWidth || document.documentElement.clientWidth);

    return (
        rect.bottom >= 0 &&
        rect.right >= 0 &&
        rect.top <= height && 
        rect.left <= width 
    );
}


function setNodes(type, status) {
    // status should be either 'locked' or 'highlighted'
    // use classList.add etc because jQuery does not
    // support modifying properties of SVG elements
    // (actually jquery 2.2.0 now supports it)
    
    var func = function(index, elem) {
        elem.classList.add(status);
    };
    
    // escape '*' found in type names
    type = type.replace( /(\*)/g, '\\$1' );
    $('.derivation').find('[rule='+type+']').each(function(index, elem) {
        if (status == 'highlighted' && !isElementInViewport(elem))
            return;
            
        var $elem = $(elem);
        $elem.find('.svg-node-text').each(func);
        $elem.find('.svg-line').each(func);
        $elem.find('text').first().each(func);
    });
}


function applyToMatchingItems(typeName, func, filterOut){
    // for each item, if any of its active derivations has 'typeName' in
    // derivation.types, func is evaluated with the jQuery element of the
    // matching item as the sole argument. items with multiple active matching
    // derivations will then have func applied to them multiple times.
    $('.item').each(function(index, element) {
        var $item = $(element);
        $item.find('.derivation.active').each(function(index, element) {
            var derivation = getDerivation($(element));
            var hasType = _.has(derivation.types, typeName); 
            if ((hasType && !filterOut) || (!hasType && filterOut))
                func($item);
        });
    });
}

function applyToNonMatchingItems(typeName, func){
    // call applyToMatchingItems in filterOut mode
    applyToMatchingItems(typeName, func, true);
}


function activateType($type, status){
    status = status || 'highlighted';
    var typeName = $type.find('.type-name').html();
    var isSignType = $type.hasClass('sign');
    
    // highlight items with this type:
    var func = function ($item){
        $item.css({'background-color': '#A6C1FF'});
    }; 

    applyToMatchingItems(typeName, func);

    if (isSignType) {
        // this is a sign type so highlight all corresponding
        // subtrees then highlight corresponding span in
        // surface string
        setNodes(typeName, status);            
        highlightSpans(typeName);
    }
}


function deactivateType(){
    // restore background
    $('.item').css({'background-color': 'white'});

    // restore tree subtrees to original colour...

    $('.highlighted').each(function(index, elem) {
        elem.classList.remove('highlighted');
    });

    $('.locked').each(function(index, elem) {
        elem.classList.remove('locked');
    });

    resetSpans();
}


function applyActiveHighlights(status) {
    status = status || 'highlighted';

    //deactivate all highlights
    deactivateType();
    // now reactivate any other active types
    $('.type.active').each(function(index, element) {
        activateType($(element), status);                
    });
}


function setTypeHandlers() {

    $('#type-table .type').hover(
        function(event) {
            if (!$(this).hasClass('active'))
                activateType($(this));
        }, 
        function(event) {
            applyActiveHighlights('locked');
        }
    );
        
    $('#type-table .type:not(.super) .type-name').click(function(event) {
        event.stopPropagation();
        var $type = $(this).parent();
        
        $type.toggleClass('active');
        applyActiveHighlights('locked');
        toggleTrees();
    });

    $('.type .filter-type-out').click(function(event) {
        // add the type name to the blacklist and apply the filter
        event.stopPropagation();
        BLACKLISTTYPES.push($(this).parent().find('.type-name').text());
        applyFilters();
    });

    $('.type .filter-type-in').click(function(event) {
        // add the type name to the whitelist and apply the filter
        event.stopPropagation();
        WHITELISTTYPES.push($(this).parent().find('.type-name').text());
        applyFilters();
    });

    var enableFunc = function($item){
        var item = getItemObject($item);
        item.disabled = false;
        $item.show();
    };

    $('#black-filter-list .type .del').click(function(event) {
        event.stopPropagation();
        var $elem = $(this).parent().remove();
        var typeName = $elem.text(); 
        BLACKLISTTYPES.splice(BLACKLISTTYPES.indexOf(typeName, 1));
        applyToMatchingItems(typeName, enableFunc);
        applyFilters();
        updateUrl();
    });

    $('#white-filter-list .type .del').click(function(event) {
        event.stopPropagation();
        var $elem = $(this).parent().remove();
        var typeName = $elem.text(); 
        WHITELISTTYPES.splice(WHITELISTTYPES.indexOf(typeName, 1));
        applyToNonMatchingItems(typeName, enableFunc);
        applyFilters();
        updateUrl();
    });

    $('#clear-filters').click(function(event) {
        event.stopPropagation();
        WHITELISTTYPES = Array();
        BLACKLISTTYPES = Array();

        // enable all items not manually disabled
        $('.item').has('.fa-toggle-on').each(function(index, element) {
            enableFunc($(element));
        });
        doDiff();
        updateUrl();
    });

    $('.type .nec-ann').click(function(event) {
        event.stopPropagation();
        var typeName = $(this).parent().find('.type-name').text();
        addNecAnnotation(typeName);
    });

    $('.type .rel-ann').click(function(event) {
        event.stopPropagation();
        var typeName = $(this).parent().find('.type-name').text();
        addRelAnnotation(typeName);
    });
}


function applyFilters() {
    // note that  if there are no filters, this function will just do a doDiff()
    var disableFunc = function($item){
        var item = getItemObject($item);
        item.disabled = true;
        $item.hide();
    };

    for (var i=0; i < BLACKLISTTYPES.length; i++)
        applyToMatchingItems(BLACKLISTTYPES[i], disableFunc);

    for (var j=0; j < WHITELISTTYPES.length; j++)
        applyToNonMatchingItems(WHITELISTTYPES[j], disableFunc);
        
    doDiff();
}


function setTreeHandlers($item) {
    $item.find('.svg-node-text').each(function(index, elem) {
        var $elem = $(elem);
        var str = $elem.attr('label');
        $elem.tooltip({
            tooltipClass : 'node-label',
            content : function() {
                var $this = $(this);
                var grammar = GRAMMARS[$item.attr('grammar')];
                var label = $this.attr('title');
                var rule = $this.parent().attr('rule');      
                var itemIsLex = label == rule;
                var treebankAlias = $('select[name=treebank-name]').val();                    
                var haveTreebank = treebankAlias != 'none';

                var makeDiv = function(name, value) {
                    return '<div class="ttline"><div class="ttname">'+name+'</div><div class="ttval">'+value+'</div></div>';
                };

                var lines = [makeDiv('Label', label)];

                if (!itemIsLex) {
                    lines.push(makeDiv('Type', rule));
                }

                if (haveTreebank) {
                    var treebank = TREEBANKS[treebankAlias];
                    var ruleStats = treebank.data[rule];

                    if (ruleStats == undefined)
                        var items = 0;
                    else
                        var items = treebank.data[rule].items;

                    var coverage = items*100/treebank.trees; 
                    lines.push(makeDiv('Coverage', coverage.toFixed(2)+'%'));

                    if (LONGLABELS)
                        var nodeQuery = rule;
                    else
                        var nodeQuery = label;

                    var links = [];  
                    var fangornUrl = makeFangornQueryUrl(treebankAlias, '//' + nodeQuery);
                    links.push(linkify(fangornUrl, 'node', 'fangorn search for this node'));

                    if (itemIsLex && grammar.ltdblink != null) {
                        links.push(linkify(grammar.ltdblink+'/description.cgi?type='+label, 'lextypeDB'));
                    } else {
                        var makeSubtreeQuery = function(node, query) {
                            var label = node.find('>text').attr('title');
                            var rule = $this.attr('rule');

                            if (LONGLABELS)
                                var nodeQuery = rule;
                            else
                                var nodeQuery = label;

                            var daughters = node.find('>g');
                            if (daughters.length == 0) {
                                return query;
                            } else if (daughters.length == 1) {
                                return query + '/' + nodeQuery + makeSubtreeQuery(daughters, '');
                            } else if (daughters.length == 2) {
                                var left = makeSubtreeQuery($(daughters[0]), '');
                                var right = makeSubtreeQuery($(daughters[1]), '');
                                return query + '/' + nodeQuery + '[' + left + ']' + right;
                            }
                            // TODO missing return value here
                        };
                        var subtreeQuery = makeSubtreeQuery($this.parent(), '/');
                        var fangornUrl = makeFangornQueryUrl(treebankAlias, subtreeQuery);
                        links.push(linkify(fangornUrl, 'subtree', 'Fangorn search for this subtree'));
                    }
                    lines.push(makeDiv('Links', links.join(' ')));
                }
                return lines.join('');
            },
            close: function(event, ui ) {
                ui.tooltip.hover(
                    function () {
                        $(this).stop(true).fadeTo(400, 1); 
                    },
                    function () {
                        $(this).fadeOut("400", function(){ $(this).remove(); });
                    }
                );
            }
        });
    });

    $item.find('.svg-node-text').hover(
        function(event) {
            var type = $(this).parent().attr('rule');
            if (type != undefined) {
                setNodes(type, 'highlighted');
            }
        }, 
        function(event) {
            var type = $(this).parent().attr('rule');
            $('.highlighted').each(function(index, elem) {
                elem.classList.remove('highlighted');
            });
        }
    );
}


function setItemHandlers($item) {

    $item.find('.derivation').click(function(event) {
        var $derivation = $(this);
        var item = getItem($item);
        var id = getDerivationId($derivation);
        var derivation = item.readings[id];

        if (event.which == 2) {
            event.stopPropagation();
            var $mrsBox = $item.find('.mrs-box');
            $mrsBox.find('.mrs-label').html('Reading ' + (id + 1));
            $mrsBox.find('.mrs').html(derivation.mrs);
            $mrsBox.show();
            return; 
        }

        if (!event.ctrlKey) {
            // Control was not held (which would make the toggle
            // additive), so deactivate all *other* trees.
            $item.find('.derivation').removeClass('active');
            for (var i=0; i < item.readings.length; i++) {
                item.readings[i].active = false;
            }
        }            

        derivation.active = !derivation.active;
        $derivation.toggleClass('active');
        doDiff();
    });

    $item.find('.activate-derivations').click(function(event) {
        var item = getItem($item);
        $item.find('.derivation').addClass('active');

        for (var i=0; i < item.readings.length; i++) {
            item.readings[i].active = true;
        }
        doDiff();
    });

    $item.find('.disable-derivations').click(function(event) {
        var item = getItem($item);
        $item.find('.derivation').removeClass('active');

        for (var i=0; i < item.readings.length; i++) {
            item.readings[i].active = false;
        }
        doDiff();
    });

    $item.find('.toggle-tree-box').click(function(event) {
        var $this = $(this);
        var val = $this.val();
        var $treeBox = $item.find('.tree-box:first');
        
        $treeBox.toggleClass('max');

        if (val == 'Maximise') {
            $this.val('Minimize');
        } else {
            $this.val('Maximise');
        }
    });

    $item.find('.copy-item').click(function(event) {
        var type = getItemType($item);
        var newType = type  == 'pos' ? 'neg' : 'pos';
        var newItems = getItems(newType);
        var $newItems = $('#'+newType+'-items .item-list');
        var newItem = $.extend(true, {}, getItem($item));

        // first disable the other items from the other set
        $newItems.find('.item .disable').each(function (index, elem) {
            $elem = $(elem);
            if (!getItem($elem.closest('.item')).disabled) 
                $elem.trigger('click');
        });

        // then copy the item to the other set
        var $newItem = $item.clone().appendTo($newItems);
        var i = incrCounter(newType);

        $newItem.find('.popup').hide();
        setItemHandlers($newItem);
        setTreeHandlers($newItem);
        newItems.push(newItem);
        $newItem.attr('id', newType+'-item-'+ i).find('.number').html(i+1);
        doDiff();
        $('.item-type').show();
    });

    $item.find('.popup').click(function(event){
        event.stopPropagation();
        if ($(this).hasClass('tree-box')) {
            $(this).parent().find('.mrs-box').hide();
        }
    });

    $item.find('.disable').click(function(event) {
        event.stopPropagation();
        var item = getItemObject($item);
        item.disabled = !item.disabled;
        $(this).children().toggleClass('fa-toggle-on fa-toggle-off');
        $item.toggleClass('disabled');
        doDiff();
    });

    $item.click(function(event) {
        // Draw the trees on clicking on an item.  (Do on click
        // because rendering is messed up if we do it earlier?)
        event.stopPropagation();
        var $treeBox = $item.find('.tree-box');
        $('.popup').hide();

        if ($treeBox.is(':visible'))
            $treeBox.hide();
        else
            $treeBox.show();

        // if we've already drawn the trees, return
        if ($item.find('.svg-node').length != 0)
            return;

        drawTrees($item);
        setTreeHandlers($item);

        // in case some of the types are already active
        applyActiveHighlights('locked');
    });


    $item.find('.actions .del').click(function(event) {
        event.stopPropagation();
        $(this).closest('.item').fadeOut(FADELENGTH, function() { 
            var $item = $(this);
            var id = getItemId($item);
            var type = getItemType($item);
            var items = getItems(type);
            decrCounter(type);
            items.splice(id, 1);
            updateIds($item);
            $item.remove(); 

            if (!havePosItems()) $('#pos-items').hide();
            if (!haveNegItems()) $('#neg-items').hide();
            setOperator();
            
            if (!haveItems()) 
                $('#clear-button').trigger('click');
            else
                doDiff();
        });
    });
}


function updateIds(removedElem) {
    removedElem.nextAll('.item').each(function(index, elem) {
        var $elem = $(elem);
        var newId = getItemId($elem) - 1;
        var type = getItemType($elem);
        $elem.attr('id', type+'-item-'+newId);
        $elem.find('.number').text(newId+1); 
    });
}


function loadData(callback) {
    var posting = $.post('/load-data');
    posting.done(function(data) {
        FANGORNPATH = data.fangornpath;
        GRAMMARS = {};
        var $grammarInput = $('#grammar-input');
        var $treebankInput = $('#treebank-input');
        var $profileInput = $('.profile-input');
        
        for (var i=0; i < data.grammars.length; i++) {
            var grammar = data.grammars[i]; 
            GRAMMARS[grammar.alias] = grammar;
            $grammarInput.append($('<option>', {
                'value' : grammar.alias,
                'html'  : grammar.shortname
            }));
        }

        TREEBANKS = {};
        for (var i=0; i < data.treebanks.length; i++) {
            var treebank = data.treebanks[i]; 
            TREEBANKS[treebank.alias] = treebank;
            $treebankInput.append($('<option>', {
                'value' : treebank.alias,
                'html'  : treebank.name
            }));
        }
        $treebankInput.append($('<option>', {'value':'none', 'html':'None'}));

        PROFILES = {};
        for (var i=0; i < data.profiles.length; i++) {
            var profile = data.profiles[i]; 
            PROFILES[profile.alias] = profile;
            $profileInput.append($('<option>', {
                'value' : profile.alias,
                'html'  : profile.name
            }));
        }

        callback();
    });
}


function clearState(callback) {
    POSITEMS = Array();
    NEGITEMS = Array();
    POSPROFILES = Array();
    NEGPROFILES = Array();
    WHITELISTTYPES = Array();
    BLACKLISTTYPES = Array();
    POSCOUNTER = 0;
    NEGCOUNTER = 0;
    updateButtons();

    var things = '#fail-box, #success-box, #pos-items, #neg-items'; 
    
    if (!callback) {
        $(things).fadeOut(FADELENGTH, function() {
            $('.item').remove();
        });

        $('#output-pane-contents').fadeOut(FADELENGTH, function() { 
            $(this).empty().show();
        } );
    } else {
        // The callback must be called after both sets of things have
        // finished being made visible again. Which means we would
        // need to wait until both sets of fading have finished.  Just
        // cludge it and remove the fading.
        $(things).hide();
        $('.item').remove();
        $('#output-pane-contents').empty();
        callback();
    }
    setOperator();
    updateUrl();
}


function setHandlers() {

    $('#toggle-help').click(function(event) {
        $('#help-content').slideToggle();
    });

    $('#add-items-button').click(function(event) {
        event.stopPropagation();
        $('.popup').hide();
        $('#add-items-box').show();
    });

    $('#help-box').click(function(event) {
        event.stopPropagation();
    });

    $('#swap-items-button').click(function(event) {

        if ($(this).hasClass('disabled')) 
            return;

        if (!haveItems()) 
            return;

        var tmpItems = NEGITEMS;
        var tmpCounter = NEGCOUNTER;
        NEGITEMS = POSITEMS;
        POSITEMS = tmpItems;
        NEGCOUNTER = POSCOUNTER;
        POSCOUNTER = tmpCounter;

        var $pos = $('#pos-items').find('.item-list');
        var $neg = $('#neg-items').find('.item-list');
        var posHtml = $pos.html();
        var negHtml = $neg.html();

        // for some reason, some of the derivation svgs are being
        // deleted/corrupted when moving, so just delete them and they
        // can be redrawn
        $pos.html(negHtml).find('.derivation').empty();
        $neg.html(posHtml).find('.derivation').empty();

        // do some things to all the items
        $pos.add($neg).find('.item').each(function (index) { 
            var $this = $(this);
            toggleItemType($this); 
            setItemHandlers($this);
        });
        doDiff();
    });

    $('#clear-button').click(function(event) {
        if ($(this).hasClass('disabled')) 
            return;
        clearState();
    });

    $('input[name=labels]').change(function(event) {
        var labels = $(this).val(); 
        updateUrl();

        if (labels == 'long')
            LONGLABELS = true;
        else
            LONGLABELS = false;

        // delete all the derivations so they get redrawn with new labels
        // with a new diff. 
        if (haveItems()) {
            $('.derivation').fadeOut(FADELENGTH, function() { 
                var $this = $(this); 
                $this.empty();
                $this.show();
                doDiff();
            } );
        }
    });
                                 
    $('input[name=supers]').change(function(event) {
        SUPERS = $(this).prop('checked');
        updateUrl();

        // TODO: I think any active filters will be lost on supers being
        // toggled.
        if (SUPERS && haveItems()) { 
            if ($('.type-line.super').length > 0)
                $('.type-line.super').show();                
            else
                clearState(loadUrlParams);
        } else {
            $('.type-line.super').hide();
        }
        
    });

    $('input[name=tagger]').change(function(event) {
        updateUrl();        
    });

    $('input[name=fragments]').change(function(event) {
        updateUrl();
    }); 

    $('#treebank-input').change(function(event) {
        doDiff();
    });

    $('#submit-items-button').click(function(event) {
        if ($('#pos-input').val() != '' ||
            $('#neg-input').val() != '') {
            $('#add-items-box').hide();
            processItems();
        }

        if ($("#pos-profile-input").val() != null ||
            $("#pos-profile-input").val() != null) {
            $('#add-items-box').hide();
            processProfiles();            
        }
    });

    $("#pos-input, #neg-input").keydown(function(event){
        var keyCode = (event.which ? event.which : event.keyCode);
        if (keyCode === 10 || keyCode == 13 && event.ctrlKey) {
            $('#submit-items-button').trigger('click');
        } else if (keyCode === 10 || keyCode == 13 && event.altKey) {
            var posInputs = `
The manager remembered having to hire and being forced to fire employees.
The manager had to hire and fire employees.
The manager hires and fires employees.`;
            var negInputs = `The manager hires employees and fires employees.`;
            $('#pos-input').val(posInputs);
            $('#neg-input').val(negInputs);
            $('#submit-items-button').trigger('click');
        }
    });

    function addPhenomenonOptions(options, $target){
        $target.find('option.phenomenon').remove();
        for (var i=0; i < options.length; i++) {
            var option = options[i];
            $target.append($(`<option class="phenomenon">${option}</option>`));
        }
        $target.closest('.phenomenon-row').css('visibility', 'visible');
    }
    
    $("#pos-profile-input").change(function (event){
        var phenomenona = PROFILES[$(this).val()].phenomena;
        if (phenomenona && phenomenona.length > 0) {
            var $target = $("#pos-profile-phenomenon");
            addPhenomenonOptions(phenomenona, $target);
        }
    });

    $("#neg-profile-input").change(function (event){
        var phenomenona = PROFILES[$(this).val()].phenomena;
        if (phenomenona && phenomenona.length > 0) {
            var $target = $("#neg-profile-phenomenon");
            addPhenomenonOptions(phenomenona, $target);
        }
    });

    $("#pos-profile-phenomenon").change(function(event){
        var phenomenon = $(this).val();
        var constraint = `p-name="${phenomenon}"`;
        $('#pos-profile-filter').val(constraint); 
    });

    $("#neg-profile-phenomenon").change(function(event){
        var phenomenon = $(this).val();
        var constraint = `p-name="${phenomenon}"`;
        $('#neg-profile-filter').val(constraint); 
    });
    
    $("body").click(function(event){
        $(".popup").hide();
        $('#help-content').slideUp();
    });

    $(".popup").click(function(event){
        event.stopPropagation();
    });

    $(".set-operator").click(function(){
        $this = $(this);

        if ($this.hasClass('enabled'))
            return;
        
        updateCompare($this.data('operator'));
        updateUrl();
        doDiff();
    });

    $('#annotate-button').click(function(event) {    
        if (!ANNOTATION_MODE) {
            loadAnnotationMode('start');
        } else{
            ANNOTATION_MODE = false;
            $('#annotation-box').hide();
        }
        updateUrl();
    });

    $('#next-annotation').click(function(event) {
        var current = ANNOTATION_LABELS.indexOf(ANNOTATION_LABEL);
        ANNOTATION_LABEL = ANNOTATION_LABELS[current + 1];
        $('#phenomenon-label').html(ANNOTATION_LABEL);
        $('#annotated-types-container .type-wrapper').remove();
        $('#annotation-comment textarea').val('');
        $('#clear-button').trigger('click');
    });
    
    $('#submit-annotation').click(function(event) {    
        var name = $('#annotation-name').val();

        if (name == ''){
            alert('Please enter your name');
            return;
        }

        var annotations = getAllAnnotations();
        
        if (annotations.length == 0) {
            alert('Need at least one type to record an annotation.');
            return;
        }

        var data = {
            'name': name,
            'label': $('#phenomenon-label').text(),
            'comment': $('#annotation-comment textarea').val(),
            'necessary-annotations': getNecAnnotations().join(','),
            'relevant-annotations': getRelAnnotations().join(','),
            'url': window.location.href
        };

        $.post('/annotate', data).done(function(data) {
            if (!data.success)
                return;
            
            var current = ANNOTATION_LABELS.indexOf(ANNOTATION_LABEL);

            if (current == ANNOTATION_LABELS.length - 1){
                $('#annotation-box').html("<h3>You're done!</h3>");
                return; 
            }
            
            $('#annotated-types-container .type-wrapper').remove();
            $('#annotation-comment textarea').val('');

        });
    });
}


$(document).ready(function(){
    $('.hidden').hide();
    loadData(loadUrlParams);
    setHandlers();
    updateCompare("union");
    updateButtons();
});
