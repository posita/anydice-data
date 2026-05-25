var hasMath = hasMath || false;
if(hasMath) {
	(function(d, t) {
		var g = d.createElement(t),
			s = d.getElementsByTagName(t)[0];
//		g.src = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=AM_HTMLorMML-full';
		g.src = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=AM_CHTML';
		s.parentNode.insertBefore(g, s);
	}(document, 'script'));
}
