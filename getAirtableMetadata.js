#!/usr/bin/env node

// https://github.com/wikitongues/Oral-History-Template-Instantiator/blob/master/single.js

'use strict';
var Airtable = require('airtable');
var fs = require('fs');
var destination = process.argv[3]

var single = process.argv[2];

try {
  var base = new Airtable({apiKey: process.env.APIKEY}).base(process.env.BASE);

  base('🍩 Oral Histories').select({
      view: ".LOCMetadataView",
      cellFormat: "string",
      timeZone: "America/New_York",
      userLocale: "en-ca",
      filterByFormula: "Identifier='"+single+"'",
      fields: [
        "Identifier",
        "Languages: ISO Code (639-3)",
        "Language names",
        "Languages: Speaker preferred names",
        "Contributor: Speakers",
        ".self?",
        "Creator",
        "Subject: Language Nation of Origin",
        "Coverage: Video Territory",
        "Description",
        "Rights",
        "Youtube Publish Date",
        "Wikimedia Eligibility",
        "Wiki Commons URL"
      ]
  }).eachPage(function page(records, fetchNextPage) {
    if (!Array.isArray(records) || !!records.length) {
      records.forEach(function(record) {
          const content = [
            `Metadata for ${record.get('Identifier')}`,

            `Oral History ID:  ${record.get('Identifier')}`,
            `Languages by ISO 639-3 Code: ${record.get('Languages: ISO Code (639-3)')}`,
            `Language Names: ${record.get('Language names')}`,
            `Alternate Names: ${record.get('Languages: Speaker preferred names')}`,
            `Speakers: ${record.get('Contributor: Speakers')}`,

            `Video Description: ${record.get('Description') || ''}`,

            `Original Submitter: ${record.get('Creator')}`,
            `Licenses: ${record.get('Rights')}`,
            `Video Nation: ${record.get('Subject: Language Nation of Origin')}`,
            `Video Territory: ${record.get('Coverage: Video Territory')}`,

            `Published to Youtube on: ${record.get('Youtube Publish Date')}`,
            `Wikimedia Status: ${record.get('Wikimedia Eligibility')}`,
            `Wiki Commons URL: ${record.get('Wiki Commons URL')}`
          ].join('\n');

          fs.writeFileSync(`${destination}/loctemp__${single}/${record.get('Identifier')}__metadata.txt`, content);
      });
      fetchNextPage();
    } else {
      console.log(`\x1b[31mWarning! ID '${single}' not found on airtable.`)
    }
  }, function done(err) {
      if (err) { 
        console.error(err); 
        return process.exit(1);
      }
  });
} catch (e) {
  console.error(e);
  return process.exit(1);
}