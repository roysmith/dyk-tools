"use strict";

// User:RoySmith/dyk-pingifier.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class Pingifier {
    constructor($, mw) {
        this.$ = $;
        this.mw = mw;
        this.updateTimes = {};
    }
}

exports.Pingifier = Pingifier;


mw.hook('wikipage.content').add(async function ($content) {
    console.log('try.js loaded');
    // If the content is not a valid jQuery object, we can't do anything.
    if (!$content.jquery) {
        console.log('not a valid jQuery object');
        return;
    }
    const pageName = mw.config.get('wgPageName');
    const dykNomPattern = new RegExp('^Template:Did_you_know_nominations/');
    if (!dykNomPattern.test(pageName)) {
        return;
    }

    const $pingBox = $('<textarea id="ping-box" rows="8"></textarea>');
    $pingBox.insertBefore('#firstHeading');
    const templateName = $('#firstHeading > span.mw-page-title-main')
        .text()
        .replace('Did you know nominations/', '');
    $pingBox.append('===[[', pageName, '|', templateName, ']]===\n');

    $.get('/wiki/Template:Did_you_know/Queue/LocalUpdateTimes', function (localUpdateTimes) {
        const queuePattern = new RegExp('(?<tag>Queue \\d)');
        const prepPattern = new RegExp('(?<tag>Prep \\d)');
        $(localUpdateTimes).find('table.wikitable > tbody > tr').each(function ($row) {
            const cells = $($(this).find('td'));
            if (cells.length < 1) {
                return;
            }
            const time = cells[3].innerHTML.replace('<br>', '&nbsp;').trim();
            const tags = $(cells[0]).text();
            var found = tags.match(queuePattern);
            if (found) {
                console.log('found queue', found.groups.tag);
                updateTimes[found.groups.tag] = time;
            }
            found = tags.match(prepPattern);
            if (found) {
                console.log('found prep', found.groups.tag);
                updateTimes[found.groups.tag] = time;
            }
        });
        console.log(updateTimes);
    });

    const $copyButton = $('<button id="copy-button">Copy</button>')
        .on('click', async function () {
            const $text = $('#ping-box').val();
            try {
                await navigator.clipboard.writeText($text);
                console.log('copied to clipboard', $text);
            } catch (error) {
                console.log('Failed to copy!', error);
                return;
            }
        });
    $copyButton.insertAfter('#ping-box');

    const $l2Button = $('<button id="l2-button">Add L2 Header</button>')
        .on('click', async function () {
            const params = {
                action: 'query',
                prop: 'linkshere',
                titles: pageName,
                format: 'json',
            };
            const api = new mw.Api();
            api.get(params)
                .done(function (data) {
                    const id = mw.config.get('wgArticleId');
                    data.query.pages[id].linkshere.forEach(function (pageData) {
                        const title = pageData.title;
                        const titlePattern = new RegExp('^Template:Did you know/Queue/(?<n>\\d+)$');
                        const match = title.match(titlePattern);
                        if (match) {
                            const key = 'Queue ' + match.groups.n;
                            $pingBox.prepend('==[[', title, '|', key, ']] (', updateTimes[key], ')==\n\n');
                        };
                    })
                });
        });
    $l2Button.insertAfter('#ping-box');

    const userSubpagePattern = new RegExp('^/wiki/User:[^/]+$');
    const $users = $content.find('a')
        .filter(function (index) {
            return userSubpagePattern.test($(this).attr('href'));
        });
    $users.each(function () {
        const $this = $(this);
        const $button = $('<button>')
            .text('ping')
            .on('click', async function () {
                const userName = $this.attr('href')
                    .replace(/^\/wiki\/User:/, '')
                    .replace(/_/g, ' ');
                $pingBox.append('{{ping|' + userName + '}}\n');
            });
        $button.insertAfter($this);
    });
});
