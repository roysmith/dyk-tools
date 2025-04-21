"use strict";

const fs = require('node:fs');
const { describe } = require('node:test');
const { DYKReviewTool } = require('./dyk_reviewTool');

describe('constructor', () => {
    it('builds a default instance', () => {
        const rt = new DYKReviewTool();
        expect(rt).toBeInstanceOf(DYKReviewTool);
    });
});
