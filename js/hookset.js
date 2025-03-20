"use strict";

const { Hook, Link } = require('./hook');

// hookset.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class HookSet {
    constructor(pageTitle) {
        this.wikitext = "";
        this.hooks = [];
    }

    async init(pageTitle) {
        await this.load(pageTitle);
        this.hooks = this.findHooks(this.wikitext);
    }

    async load(pageTitle) {
        const api = new mw.Api();
        const params = {
            action: 'parse',
            format: 'json',
            page: pageTitle,
            prop: 'wikitext',
            formatversion: 2,
        };
        const self = this;
        api.get(params)
            .then((result) => {
                const wikitext = JSON.parse(result).parse.wikitext;
                self.wikitext = wikitext;
            }, (result) => {
                console.log(result);
            });
    }

    findHooks(wikitext) {
        return this.findHookLines(wikitext).map((line) => {
            return new Hook(line);
        });
    }

    findHookLines(wikitext) {
        const m = wikitext.match(new RegExp('^<!--Hooks-->$(?<block>.*)^<!--HooksEnd-->$', 'sm'));
        return m.groups.block.split('\n')
            .filter((line) => {
                return line.startsWith('* ... ');
            });
    }
}

module.exports = { HookSet };
