"use strict";

const { Hook } = require('./hook');

// hookset.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class HookSet {
    constructor(title, wikitext, hooks, nominationMap) {
        this.title = title;
        this.wikitext = wikitext;
        this.hooks = hooks;
        this.nominationMap = nominationMap;
    }

    static async build(pageTitle) {
        const wikitext = await HookSet.loadWikitext(pageTitle);
        const hooks = HookSet.findHooks(wikitext);
        const nominationMap = HookSet.findNominations(wikitext);
        return new HookSet(pageTitle, wikitext, hooks, nominationMap);
    }

    static async loadWikitext(pageTitle) {
        const api = new mw.Api();
        const params = {
            action: 'parse',
            format: 'json',
            page: pageTitle,
            prop: 'wikitext',
            formatversion: 2,
        };
        const result = await api.get(params);
        return result.parse.wikitext;
    }

    /**
     * @returns a short name for the hookSet.  This will be a string of the form
     * "Queue 1" or "Prep 5".  It is called a key because it can be used to index
     * into data structures such as that returned by LocalUpdateTimes.
     */
    key() {
        const queuePattern = new RegExp('^Template:Did you know/(?<name>Queue)/(?<number>\\d+)$');
        const prepPattern = new RegExp('^Template:Did you know/(?<name>Prep)aration area (?<number>\\d+)$');
        const m = this.title.match(queuePattern) || this.title.match(prepPattern);
        if (m) {
            return `${m.groups.name} ${m.groups.number}`;
        };
    }

    /**
     * @param string wikitext
     * @returns a generator over Hooks
     */
    static * findHooks(wikitext) {
        const m = wikitext.match(/^<!--Hooks-->$(?<hookLines>.*)^<!--HooksEnd-->$/sm);
        for (const line of m.groups.hookLines.split('\n')) {
            if (line.startsWith('* ... ')) {
                yield Hook.build(line);
            }
        }
    }

    /**
     * @param string wikitext
     * @returns a Map mapping article titles to nomination page titles.  Note that
     * a given hook may contain multiple article links; in theory all of them should
     * map to the same nomination, but the Map just relects what is in the {{DYKmake}}
     * and/or {{DYKnom}} templates, which is not guaranteed to match reality.
     * 
     * With the possibility of multiple links per hook, multiple authors and/or
     * nominators, and nominators who are not authors, things can get messy.  If
     * there are multiple DYKmake/DYKnom templates mapping a given article, in theory
     * they should all map to the same nomination page.  If they don't, there's no
     * guarantee how we'll handle that exceptional case.
     *
     * Also note that this expects the credit templates to be formatted on a single
     * and just pattern-matches them with regexes instead of actually parsing the
     * wikitext (i.e. with Parsoid).  This sucks, but Parsoid is just too painful
     * to use.
     */
    static findNominations(wikitext) {
        const map = new Map();
        const dykMakePattern = new RegExp('^\\* {{(?<template>DYKmake.*)}}');
        for (const line of wikitext.split('\n')) {
            const m = line.match(dykMakePattern);
            if (m) {
                const [templateName, articleTitle, author, subpage] = m.groups.template.split('|');
                const [unused, nominationTitle] = subpage.split('=');
                map.set(articleTitle, nominationTitle);
            }
        }
        return map;
    }
}

module.exports = { HookSet };
