"use strict";

// link.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class Link {
    constructor(target, title) {
        this.target = target;
        this.title = title;
    }

    /**
     *
     * @param {string} linkText Full link, optionally including the square brackets
     */
    static build(linkText) {
        const [target, title = ""] = linkText
            .replace(/^\[\[/, '')
            .replace(/\]\]$/, '')
            .split('|');
        return new Link(target, title);
    }
}

module.exports = { Link };
