/*
 *
 * Typediff: A tool for exploring types used in the processing of text
 * by DELPH-IN HPSG grammars
 *
 * Author: Ned Letcher
 * http://github.com/ned2/typediff
 *
 */


var POSITEMS = Array();
var NEGITEMS = Array();
var ALLITEMS = [POSITEMS, NEGITEMS];
var POSCOUNTER = 0;
var NEGCOUNTER = 0;
var DESCENDANTS = {};
var FADELENGTH = 400;
var ACTIVE_TYPES = [];

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
function getItems(type) { return (type == 'pos') ? POSITEMS : NEGITEMS; }
function getItem($item) { return getItems(getItemType($item))[getItemId($item)]; }
function getDerivationId($deriv) { return parseInt($deriv.attr('id').split('-')[1]); }
function haveItems() { return POSITEMS.length > 0 || NEGITEMS.length > 0; }
function havePosItems() { return POSITEMS.length > 0; }
function haveNegItems() { return NEGITEMS.length > 0; }

function getDerivation($deriv) { 
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


function updateUrl() {
    if (!haveItems()) return;

    var params = []; 

    var makeParam = function(param, value) {
        return [param, '=', value].join('');
    };

    var operator = $('#extra-group-operator .set-operator.enabled').data('operator');

    params.push(makeParam('count', $('#count-input').val()));
    params.push(makeParam('treebank', $("#treebank-input").val()));
    params.push(makeParam('labels', $("input[name=labels]:checked").val()));
    params.push(makeParam('tagger', $("input[name=tagger]:checked").val()));
    params.push(makeParam('mode', operator));
    params.push(makeParam('supers', $("input[name=supers]").prop('checked')));
    params.push(makeParam('fragments', $("input[name=fragments]").prop('checked')));

    var $posItems = $('#pos-items .item .text'); 
    var $negItems = $('#neg-items .item .text'); 

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

    window.location.hash = encodeURI(params.join('&'));
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
        }
    }

    if (!(Agrammar || Bgrammar))
        return;
    
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
}


function processItems(callback) {
    showStatusBox('#waiting-box');
    var grammar =  $('#grammar-input').val();
    var loadDescendants = !Boolean(DESCENDANTS[grammar]);

    var data = {
        'query' : 'parse-types', 
        'pos-items' : $('#pos-input').val(), 
        'neg-items' : $('#neg-input').val(),
        'grammar-name' : grammar,
        'count' : $('#count-input').val(),
        'load-descendants': loadDescendants,
        'supers': $('input[name=supers]').prop('checked'),
        'tagger': $("input[name=tagger]:checked").val(),
        'fragments': $('input[name=fragments]').prop('checked')
    };
        
    var posting = $.post('/parse-types', data);
    posting.done(function(data) {
        if (data.success) {
            if (data.descendants)
                DESCENDANTS[grammar] = data.descendants;

            TYPEDATA = data.typeData;
            processItemResults(data['pos-items'], 'pos');
            processItemResults(data['neg-items'], 'neg');
            $('#pos-input, #neg-input').val('');
            setOperator();
            doDiff();
            if (callback)
                callback();
        } else {
            showStatusBox('#fail-box').html(data.error.replace(/\n/g, '<br/>'));
            updateButtons();
        }
    });
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

        if (readings > 1) { 
            $treeBox.find('.tree-actions').show();
        }

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
    var boxes = $('#status-pane .pane-content > div').hide();
    return $(id).show();
}
 

function updateButtons() {
    if (!haveItems()) {
        $('#swap-items-button').addClass('disabled');
        $('#clear-button').addClass('disabled');
    } else if (!(havePosItems() && haveNegItems())) {
        $('#swap-items-button').addClass('disabled');
        $('#clear-button').removeClass('disabled');
    } else {
        $('#swap-items-button, #clear-button').removeClass('disabled');    
    }
}


function postDiff(types, supers, itemCounts, grammar, typesToSupers, treebank) {
    /* create a new table with output types */

    var outputPane = $('#output-pane-contents').empty(); 
    var table = $('<table>').
            attr({id:'#type-table'}).
            html('<thead><tr><th>kind</th><th>Items</th><th>Treebank</th><th>Type</th></tr></thead>').
            appendTo(outputPane);
    var tbody = $('<tbody>').appendTo(table);
    
    function makeNode(type, kind, superOf) {
        var typeLine = $('<tr>', {'class' : 'type-line'});

        var typeName = $('<td>', {'text'  : type,
                                  'class' : kind + ' type',
                                  'title' : kind + ' type',
                                  'style' : 'background: ' + TYPEDATA[kind].col
                               });
        
        var stringNum = '';
        if (treebank.data && !superOf) {
            var typeStats = treebank.data[type];
            var items = typeStats == undefined ? 0 : typeStats.items*100/treebank.trees;    
            stringNum = items.toFixed(2)+'%';
            if (stringNum.length == 5) stringNum = '0' + stringNum;
        }
            
        var treebankCount = $('<td>', {
            class : 'items-stat', 
            text : stringNum,
            title : 'percent of trees in treebank this type is found in'});

        var itemCount = $('<td>', {
            class : 'items-stat', 
            text : itemCounts[type],
            title : 'number of positive items found in'});

        var typeKind = $('<td>', {
            text : kind,
            "data-order" : TYPEDATA[kind].rank});

        if (superOf) {
            typeLine.addClass('super');
            typeName.addClass('super');
            typeName.attr('title', 'supertype of ' + superOf);
            itemCount.html('');
        }
        
        typeLine.append(typeKind);
        typeLine.append(itemCount);
        typeLine.append(treebankCount);
        typeLine.append(typeName);
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

    table.DataTable({
        paging: false,
        orderFixed: [0,'asc'],
        fixedHeader: true,
        columnDefs: [{ "visible": false, "targets": 0 }]
    });

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

    showStatusBox('#success-box');
    setTypeHandlers();
    updateButtons();
    updateUrl();
}


function doDiff() {
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
    var types = _.map($('.type.active'), function (x) {return x.innerHTML});
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
    
    var func = function(index, elem) {elem.classList.add(status);};
    
    // escape '*' found in type names
    type = type.replace( /(\*)/g, '\\$1' );

    $('.derivation:visible').find('[rule='+type+']').each(function(index, elem) {
        if (status == 'highlighted' && !isElementInViewport(elem))
            return;
            
        var $elem = $(elem);
        $elem.find('.svg-node-text').each(func);
        $elem.find('.svg-line').each(func);
        $elem.find('text').first().each(func);
    });
}


function updateSignNodes() {
    $('.locked').each(function(index, elem) {
        elem.classList.remove('locked');
    });
        
    $('.sign.type.active').each(function(index, elem) {
        setNodes($(elem).html(), 'locked');
    });
}


function setTypeHandlers() {

    $('.type').hover(
        function(event) {
            var $this = $(this);
            var type = $this.html();
            // highlight items with this type:
            $('.item').each(function(index, element) {
                // for each item, if any of its active derivations has
                // 'type' in derivation.types, update its background

                var $item = $(element);
                $item.find('.derivation.active').each(function(index, element) {                    
                    var derivation = getDerivation($(element));
                    if (_.has(derivation.types, type)) {
                        $item.css({'background-color': '#A6C1FF'});
                        return false;
                    }
                    return true;
                });
            });

            if ($this.hasClass('sign')) {
                // this is a sign type so highlight all corresponding
                // subtrees then highlight corresponding span in
                // surface string
                setNodes(type, 'highlighted');            
                highlightSpans(type);
            }
        }, 
        function(event) {
            // restore background
            $('.item').css({'background-color': 'white'});

            // restore tree subtrees to original colour and remove
            // surface string highlighting
            if ($(this).hasClass('sign')) {
                $('.highlighted').each(function(index, elem) {
                    elem.classList.remove('highlighted');
                });
                resetSpans();
            }
        }
    );
        
    $('.type:not(.super)').click(function(event) {
        event.stopPropagation();
        if ($(this).toggleClass('active').hasClass('sign'))
            updateSignNodes();
        toggleTrees();
    });
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
        var id = getItemId($item);
        var type = getItemType($item);
        var items = getItems(type);
        var item = items[id];
        item.disabled = !item.disabled;
        $item.toggleClass('disabled');
        $(this).find('.icon').toggle();
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
        updateSignNodes();
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

        for (var i=0; i < data.grammars.length; i++) {
            var grammar = data.grammars[i]; 
            GRAMMARS[grammar.alias] = grammar;
            $grammarInput.append($('<option>', { 'value' : grammar.alias,
                                                 'html'  : grammar.shortname
                                               }));
        }

        TREEBANKS = {};
        for (var i=0; i < data.treebanks.length; i++) {
            var treebank = data.treebanks[i]; 
            TREEBANKS[treebank.alias] = treebank;
            $treebankInput.append($('<option>', { 'value' : treebank.alias,
                                                  'html'  : treebank.name
                                               }));
        }

        $treebankInput.append($('<option>', {'value':'none', 'html':'None'}));
        callback();
    });
}


function clearState(callback) {
    POSITEMS = Array();
    NEGITEMS = Array();
    POSCOUNTER = 0;
    NEGCOUNTER = 0;
    updateButtons();

    var things = '#fail-box, #success-box, #pos-items, #neg-items'; 
    
    if (!callback) {
        $(things).fadeOut(FADELENGTH, function() {
            $('.item').remove();
        });

        $('#output-box').fadeOut(FADELENGTH, function() { 
            $(this).empty().show();
        } );
    } else {
        // The callback must be called after both sets of things have
        // finished being made visible again. Which means we would
        // need to wait until both sets of fading have finished.  Just
        // cludge it and remove the fading.
        $(things).hide();
        $('.item').remove();
        $('#output-box').empty();
        callback();
    }
    setOperator();
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
        window.location.hash = '';
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
        $('#add-items-box').hide();
        processItems();
    });

    $("#pos-input, #neg-input").keydown(function(event){
        var keyCode = (event.which ? event.which : event.keyCode);
        if (keyCode === 10 || keyCode == 13 && event.ctrlKey) {
            $('#submit-items-button').trigger('click');
        } else if (keyCode === 10 || keyCode == 13 && event.altKey) {
            $('#pos-input').val("We relied on and hired consultants.");
            $('#neg-input').val("We relied on consultants and hired consultants.");
            $('#submit-items-button').trigger('click');
        }
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
}


$(document).ready(function(){
    $('.hidden').hide();
    loadData(loadUrlParams);
    setHandlers();
    updateCompare("union");
});
