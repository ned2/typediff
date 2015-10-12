DAUGHTER_HSPACE=10
DAUGHTER_VSPACE=20


function svgelement(type) {
	return document.createElementNS("http://www.w3.org/2000/svg", 'svg:'+type);
}


function line(x1, y1, x2, y2) {
	var l = svgelement("line");
	l.setAttributeNS(null, "x1", x1);
	l.setAttributeNS(null, "x2", x2);
	l.setAttributeNS(null, "y1", y1);
	l.setAttributeNS(null, "y2", y2);
    l.setAttributeNS(null, "class", "svg-line");
	return l;
}


function text(svg, str) {
	var t = svgelement("text");
    t.setAttributeNS(null, "class", "svg-node-text");
	t.appendChild(document.createTextNode(str));
	svg.appendChild(t);
	var bbx = t.getBBox();
	svg.removeChild(t);
	t.bbx = bbx;
	return t;
}


function render_yield(svg, str) {
	var y = text(svg, str);
	y.setAttributeNS(null, "y", y.bbx.height * 2/3);
	var g = svgelement("g");
	g.appendChild(y);
	g.mywidth = y.bbx.width;
	return g;
}


function render_text(str, t) {
    // if token mapping is not on, we can't use the t.from and
    // t.to fields, so we just make do with the identifier of
    // lexical entry
    if (t.from == -1 || t.to == -1)
        return t.lexident;
    else
        return str.slice(t.from, t.to);
}


function render_tree(svg, str, t, longlabels) {
	var	dtrs = [];
	var wtot = -DAUGHTER_HSPACE;
	var dtr_label_mean = 0;

    if (longlabels) {
        var label = t.label
        var title = t.shortlabel;
    } else {
        var label = t.shortlabel;
        var title = t.label;
    }

	for(var x in t.daughters) {
		wtot += DAUGHTER_HSPACE;
		dtrs[x] = render_tree(svg, str, t.daughters[x], longlabels);
		dtr_label_mean += wtot + dtrs[x].labelcenter;
		wtot += dtrs[x].mywidth;
	}

	var lexical;

	if(dtrs.length) {
		dtr_label_mean /= dtrs.length;
	} else {
		lexical = render_yield(svg, render_text(str, t));
		wtot = lexical.mywidth;
		dtr_label_mean = wtot / 2;
	}

	var dtrs_wtot = wtot;
	var g = svgelement("g");
	var n = text(svg, label);
    g.setAttributeNS(null, "class", "svg-node");
    n.setAttributeNS(null, "title", title);

    if (t.rule) 
        g.setAttributeNS(null, "rule", t.rule);
    else 
        g.setAttributeNS(null, "rule", t.label);

	var nw = n.bbx.width;
	var nh = n.bbx.height;
	var labelcenter = dtr_label_mean;

	if(labelcenter - nw/2 < 0) labelcenter = nw/2;
	if(labelcenter + nw/2 > wtot) labelcenter = wtot - nw/2;
	if(nw > wtot) { wtot = nw; labelcenter = wtot / 2; }

	n.setAttributeNS(null, "x", labelcenter - nw / 2);
	n.setAttributeNS(null, "y", nh * 2/3);
	g.appendChild(n);

	var	dtr_x = wtot / 2 - dtrs_wtot / 2;
	var ytrans = nh + DAUGHTER_VSPACE;

	for(var x in dtrs) {
        var tvalue = "translate(" + dtr_x + "," + ytrans + ")";
        var yline = nh + DAUGHTER_VSPACE - 1;
		dtrs[x].setAttributeNS(null, "transform", tvalue);
		g.appendChild(line(labelcenter, nh, dtr_x + dtrs[x].labelcenter, yline));
		g.appendChild(dtrs[x]);
		dtr_x += dtrs[x].mywidth + DAUGHTER_HSPACE;
	}

	if(lexical) {
        var tvalue = "translate(" + dtr_x + "," + ytrans + ")";
        var yline = nh + DAUGHTER_VSPACE - 1;
		lexical.setAttributeNS(null, "transform", tvalue);
        lexical.setAttributeNS(null, "class", "leaf");
		g.appendChild(line(labelcenter, nh, wtot/2, yline));
		g.appendChild(lexical);
	}

	g.mywidth = wtot;
	g.labelcenter = labelcenter;
	g.labelheight = nh;
	t.mainsvg = g;
	t.labelsvg = n;

	return g;
}
