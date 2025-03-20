"use strict";

// hook.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class Link {
    /**
     * 
     * @param {string} link Full link, optionally including the square brackets
     */
    constructor(link) {
        const [target, title = ""] = link
            .replace(/^\[\[/, '')
            .replace(/\]\]$/, '')
            .split('|');
        this.target = target;
        this.title = title;
    }
}

class Hook {
    constructor(text) {
        this.text = text;
        this.links = this.findBoldedLinks(text);
    }

    findBoldedLinks(text) {
        let s = text;
        const pattern = new RegExp("^.*?'''(?<link>\\[\\[.*?\]\])'''(?<remainder>.*)$");
        const links = [];
        let m = null;
        while (m = s.match(pattern)) {
            links.push(new Link(m.groups.link));
            s = m.groups.remainder;
        }
        return links;
    }
}

module.exports = { Hook, Link };
