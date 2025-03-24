"use strict";

// hook.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

const { Link } = require('./link');


class Hook {
    constructor(hookText, links) {
        this.text = hookText;
        this.links = links;
    }

    static build(hookText) {
        const links = Hook.findBoldedLinks(hookText);
        return new Hook(hookText, links);
    }

    static findBoldedLinks(hookText) {
        let s = hookText;
        const pattern = new RegExp("^.*?'''(?<link>\\[\\[.*?\]\])'''(?<remainder>.*)$");
        const links = [];
        let m = null;
        while (m = s.match(pattern)) {
            links.push(Link.build(m.groups.link));
            s = m.groups.remainder;
        }
        return links;
    }
}

module.exports = { Hook };
