## history-967196 | 2024-01-26 | rev 13 | Gunter Van de Velde | history.html:1058

Request closed, assignment withdrawn: Jon Mitchell Last Call OPSDIR review

## history-967195 | 2024-01-26 | rev 13 | Gunter Van de Velde | history.html:1067

Closed request for Last Call review by OPSDIR with state 'Overtaken by Events': Cleaning up stale OPSDIR queue

## history-848980 | 2022-03-04 | rev 13 | (System) | history.html:1076

RFC Editor state changed to AUTH48-DONE from AUTH48

## history-820038 | 2021-08-05 | rev 13 | (System) | history.html:1085

RFC Editor state changed to AUTH48

## history-816261 | 2021-07-15 | rev 13 | (System) | history.html:1094

RFC Editor state changed to RFC-EDITOR from EDIT

## history-812744 | 2021-06-28 | rev 13 | (System) | history.html:1103

IANA Action state changed to RFC-Ed-Ack from Waiting on RFC Editor

## history-812502 | 2021-06-25 | rev 13 | (System) | history.html:1112

IANA Action state changed to Waiting on RFC Editor from In Progress

## history-812499 | 2021-06-25 | rev 13 | (System) | history.html:1121

IANA Action state changed to In Progress from Waiting on Authors

## history-812436 | 2021-06-24 | rev 13 | (System) | history.html:1130

IANA Action state changed to Waiting on Authors from In Progress

## history-812166 | 2021-06-22 | rev 13 | (System) | history.html:1139

RFC Editor state changed to EDIT

## history-812165 | 2021-06-22 | rev 13 | (System) | history.html:1148

IESG state changed to RFC Ed Queue from Approved-announcement sent

## history-812164 | 2021-06-22 | rev 13 | (System) | history.html:1157

Announcement was received by RFC Editor

## history-812158 | 2021-06-22 | rev 13 | (System) | history.html:1166

IANA Action state changed to In Progress

## history-812146 | 2021-06-22 | rev 13 | (System) | history.html:1175

Removed all action holders (IESG state changed)

## history-812145 | 2021-06-22 | rev 13 | Cindy Morgan | history.html:1184

IESG state changed to Approved-announcement sent from Approved-announcement to be sent

## history-812144 | 2021-06-22 | rev 13 | Cindy Morgan | history.html:1193

IESG has approved the document

## history-812143 | 2021-06-22 | rev 13 | Cindy Morgan | history.html:1202

Closed "Approve" ballot

## history-812142 | 2021-06-22 | rev 13 | Cindy Morgan | history.html:1211

Ballot approval text was generated

## history-812141 | 2021-06-22 | rev 13 | Benjamin Kaduk | history.html:1220

IESG state changed to Approved-announcement to be sent from Approved-announcement to be sent::AD Followup

## history-812133 | 2021-06-22 | rev 13 | Thomas Fossati | history.html:1229

New version available: draft-ietf-tls-dtls-connection-id-13.txt

## history-812132 | 2021-06-22 | rev 13 | (System) | history.html:1238

New version approved

## history-812131 | 2021-06-22 | rev 13 | (System) | history.html:1247

Request for posting confirmation emailed to previous authors: Achim Kraus , Eric Rescorla , Hannes Tschofenig , Thomas Fossati

## history-812130 | 2021-06-22 | rev 13 | Thomas Fossati | history.html:1256

Uploaded new revision

## history-806432 | 2021-05-11 | rev 12 | (System) | history.html:1265

Sub state has been changed to AD Followup from Revised ID Needed

## history-806431 | 2021-05-11 | rev 12 | Hannes Tschofenig | history.html:1274

New version available: draft-ietf-tls-dtls-connection-id-12.txt

## history-806430 | 2021-05-11 | rev 12 | (System) | history.html:1283

New version approved

## history-806429 | 2021-05-11 | rev 12 | (System) | history.html:1292

Request for posting confirmation emailed to previous authors: Achim Kraus , Eric Rescorla , Hannes Tschofenig , Thomas Fossati

## history-806428 | 2021-05-11 | rev 12 | Hannes Tschofenig | history.html:1301

Uploaded new revision

## history-804392 | 2021-04-22 | rev 11 | Daniel Franke | history.html:1310

Request for Last Call review by SECDIR Completed: Ready. Reviewer: Daniel Franke. Sent review to list.

## history-804363 | 2021-04-22 | rev 11 | (System) | history.html:1319

Changed action holders to Eric Rescorla, Hannes Tschofenig, Thomas Fossati, Achim Kraus (IESG state changed)

## history-804362 | 2021-04-22 | rev 11 | Cindy Morgan | history.html:1328

IESG state changed to Approved-announcement to be sent::Revised I-D Needed from IESG Evaluation

## history-804344 | 2021-04-22 | rev 11 | Lars Eggert | history.html:1337

[Ballot comment]
All comments below are about potential very minor issues that you may choose to
address in some way - or ignore - as you see fit. Some were flagged by
automated tools, so there will likely be some false positives. There is no need
to let me know what you did with these suggestions. 

Section 3, paragraph 10, nit:
> the record format defined in {{dtls-ciphertext} with the new MAC

Broken kramdown reference?

Section 1, paragraph 4, nit:
- This document defines an extension to DTLS 1.2 to add a CID to the
+ This document defines an extension to DTLS 1.2 to add a Connection ID (CID) to the
+ ++++++++++ ++++++

Section 3, paragraph 7, nit:
- for example by having the length in question be a compile-time
+ for example, by having the length in question be a compile-time
+ +

Section 3, paragraph 7, nit:
- different length to other parties. Implementations that want to use
- variable-length CIDs are responsible for constructing the CID in such
+ different lengths to other parties. Implementations that want to use
+ +
+ variable-length CIDs are responsible for constructing the CIDs in such
+ +

Section 3, paragraph 12, nit:
- datagram with the RFC 6347-defined record format the MAC calculation
+ datagram with the RFC 6347-defined record format, the MAC calculation
+ +

Section 4, paragraph 6, nit:
- * The true content type is inside the encryption envelope, as
- - -
+ * The real content type is inside the encryption envelope, as
+ ++

Section 6, paragraph 2, nit:
- datagram unless the following three conditions are met:
+ datagram, unless all of the following three conditions are met:
+ + +++++++

Section 10, paragraph 2, nit:
- This document requests three actions by IANA.
- ^^
+ This document requests three actions from IANA.
+ ^^^^

Section 4, paragraph 17, nit:
> cord. outer_type The outer content type of a DTLSCiphertext record carrying a 
> ^^^^^^^^^
If 'type' is a classification term, 'a' is not necessary. Use "type of". (The
phrases 'kind of' and 'sort of' are informal if they mean 'to some extent'.)

Section 4, paragraph 19, nit:
> the CID value it will receive and use to identify the connection, so an implemen
> ^^^^^^
Make sure that 'use to' is correct. For habitual actions in the past or to mean
'accustomed to', use "used to".

Section 5, paragraph 6, nit:
> Plaintext The length (in bytes) of the serialised DTLSInnerPlaintext (two-byte inte
> ^^^^^^^^^^
Do not mix variants of the same word ('serialise' and 'serialize') within a
single text.

Section 6, paragraph 2, nit:
> that has a source address different than the one currently associated with the D
> ^^^^
Did you mean 'different "from"? 'Different than' is often considered colloquial
style.

Section 6, paragraph 2, nit:
> ied in the received datagram, unless all of the following three conditions are met: 
> ^^^^^^^^^^
Consider using "all the".

"Appendix A.", paragraph 1, nit:
> History RFC EDITOR: PLEASE REMOVE THE THIS SECTION draft-ietf-tls-dtls-connect
> ^^^^^^^^
Maybe you need to remove the second determiner so that only "THE" or "THIS" is
left.

"Appendix A.", paragraph 29, nit:
> 2 * Move to internal content types a la DTLS 1.3. draft-ietf-tls-dtls-conne
> ^^^^
'a la' is an imported foreign expression, which originally has a diacritic.
Consider using "à la"

"Appendix B.", paragraph 1, nit:
> formation RFC EDITOR: PLEASE REMOVE THE THIS SECTION The discussion list for the
> ^^^^^^^^
Maybe you need to remove the second determiner so that only "THE" or "THIS" is
left.

"Appendix C.", paragraph 1, nit:
> Many people have contributed to this specification and we would like to thank the following
> ^^^^^^^^^^^^^^^^^
Use a comma before 'and' if it connects two independent clauses (unless they
are closely connected and short).

These reference issues exist in the document:
 * No reference entries found for: 
 [ChangeCipherSpec], [length], [length_of_padding],
 [DTLSCiphertext.length],
 [draft-rescorla-tls-dtls-connection-id-00],
 [cid_length], [DTLSPlaintext.length]
 * Uncited references: [RFC5246]
 * Obsolete reference to RFC5246, obsoleted by RFC8446

These URLs in the document did not return content:
 * https://www1.ietf.org/mailman/listinfo/tls
 * http://www.ietf.org/internet-drafts/draft-tschofenig-tls-dtls-rrc-01.txt
 * http://www.ietf.org/internet-drafts/draft-ietf-tls-dtls13-40.txt

## history-804343 | 2021-04-22 | rev 11 | Lars Eggert | history.html:1346

[Ballot Position Update] New position, No Objection, has been recorded for Lars Eggert

## history-804337 | 2021-04-22 | rev 11 | Zaheduzzaman Sarker | history.html:1355

[Ballot Position Update] New position, No Objection, has been recorded for Zaheduzzaman Sarker

## history-804247 | 2021-04-22 | rev 11 | Murray Kucherawy | history.html:1364

[Ballot comment]
I concur with my colleagues that this was easy to understand. Nice work.

I do get a little nervous these days at shepherd writeups that are over a year old.

## history-804246 | 2021-04-22 | rev 11 | Murray Kucherawy | history.html:1373

[Ballot Position Update] New position, No Objection, has been recorded for Murray Kucherawy

## history-804038 | 2021-04-20 | rev 11 | Roman Danyliw | history.html:1382

[Ballot Position Update] New position, No Objection, has been recorded for Roman Danyliw

## history-804020 | 2021-04-20 | rev 11 | Erik Kline | history.html:1391

[Ballot Position Update] New position, Yes, has been recorded for Erik Kline

## history-804004 | 2021-04-20 | rev 11 | Warren Kumari | history.html:1400

[Ballot comment]
I opened this document with much trepidation -- I was expecting it to be horribly complex to read, and requiring much understanding of DTLS... but I was pleasantly surprised by just how readable / understandable it was.

I did find "Because each party sends the value in the "connection_id" extension it wants to receive as a CID in encrypted records, it is possible for an endpoint to use a globally constant length for such connection identifiers. " to be confusing. I was trying to figure out what *the* globally constant length is; global implied to me that everyone would use it. Could this be reworded to something like "for an endpoint to use a constant length for all such connection identifiers." or similar?

## history-804003 | 2021-04-20 | rev 11 | Warren Kumari | history.html:1409

[Ballot Position Update] New position, No Objection, has been recorded for Warren Kumari

## history-803988 | 2021-04-20 | rev 11 | John Scudder | history.html:1418

[Ballot comment]
I found this document heavy sledding but once I was through it, it all came together, with the exception of my #3, below. The “heavy sledding” part I think would be largely fixed by addressing my #1, below.

1. Section 3:

This pseudocode is a little too pseudo for me:

 struct {
 opaque cid<0..2^8-1>;
 } ConnectionId;

What does the content of the angle brackets mean? At first I took it to mean “this can take on a value from 0 to 255” [*] but parts of the spec that go on about variable lengths made me think that couldn’t be right. Eventually, by paging through RFC 5246, I found some explanations of what this stuff is supposed to mean; in §4.3 of that RFC I found out that 

 Variable-length vectors are defined by specifying a subrange of legal
 lengths, inclusively, using the notation . When
 these are encoded, the actual length precedes the vector's contents
 in the byte stream. The length will be in the form of a number
 consuming as many bytes as required to hold the vector's specified
 maximum (ceiling) length.

I assume this is what’s going on in DTLS as well. This cleared up my main source of confusion, which was regarding just how you were encoding these variable-length CIDs anyway. (And oh by the way, that definition doesn’t say what the units of length are. Bytes seems implied but isn’t explicit.)

While I don’t expect you to supply these definitions again, it would be courteous to your readers to have a sentence or two explaining that pseudo-code conventions are found in RFC 5246, special extra credit for section references as well. And yes, I did notice "This document assumes familiarity with DTLS 1.2 [RFC6347].” That’s well and good, but I don’t think “familiarity” is the same as “we have adopted the same notational conventions”. 

[*] By the way, why not just use “255” in the text instead of “2^8-1”? Eschew obfuscation!


2. Section 3:

 If DTLS peers have negotiated the use of a non-zero-length CID for a
 given direction, then once encryption is enabled they MUST send with
 the record format defined in {{dtls-ciphertext} with the new MAC
 computation defined in Section 5 and the content type tls12_cid.
 Plaintext payloads never use the new record type and the CID content
 type.

What’s “{{dtls-ciphertext}”? I’m guessing just a botched xref? 

Also, the first sentence seems to have no object. (What MUST they send?)


3. Section 6:

 * There is a strategy for ensuring that the new peer address is able
 to receive and process DTLS records. No such strategy is defined
 in this specification.

This is a little mind-boggling to me. I understand this to mean I can’t send the new address a DTLS record unless I’ve already ensured it can receive and process that record, right? This seems almost like a classic Catch-22. I feel like I must be missing something.

## history-803987 | 2021-04-20 | rev 11 | John Scudder | history.html:1427

[Ballot Position Update] New position, No Objection, has been recorded for John Scudder

## history-803968 | 2021-04-20 | rev 11 | Martin Duke | history.html:1436

[Ballot comment]
Thanks for this document.

Section 9.3.3 of quic-transport, which deals with basically the same security model, also requires the receiving endpoint to probe the original address, not just the new one, to address a somewhat more difficult attack. It would be good to at least RECOMMEND this behavior for DTLS applications, and/or (repeat/informatively reference) the logic there.

## history-803967 | 2021-04-20 | rev 11 | Martin Duke | history.html:1445

[Ballot Position Update] New position, No Objection, has been recorded for Martin Duke

## history-803932 | 2021-04-20 | rev 11 | Francesca Palombini | history.html:1454

[Ballot comment]
Thank you for the work on this document. I only have minor comments and nits below.

Francesca


1. -----

 sending messages to the client. A zero-length CID value indicates
 that the client is prepared to send with a CID but does not wish the
 server to use one when sending.

...

 to use when sending messages towards it. A zero-length value
 indicates that the server will send with the client's CID but does
 not wish the client to include a CID.

FP: clarification question: I am not sure the following formulation is very clear to me: "to send with a(/the client's) CID". Could "send with" be rephrased to clarify? The previous paragraph uses "using a CID value", that would be better IMO.

2. -----

 the record format defined in {{dtls-ciphertext} with the new MAC

FP: nit - missing "}" in markdown.

3. -----

 The following MAC algorithm applies to block ciphers that use the
 with Encrypt-then-MAC processing described in [RFC7366].

FP: remove "with"

4. -----

Section 10.1

FP: I believe you should specify 1. what allowed values are for this column (i.e. Y or N, and what they mean) and 2. what happens to the existing entries - namely that they all get "N" value.

5. -----

Section 10.2 

FP: Just checking - why is 53 "incompatible with this document"?

6. -----

 Value Extension Name TLS 1.3 DTLS Only Recommended Reference

FP: nit- s/DTLS Only/DTLS-Only to be consistent with 10.1

## history-803931 | 2021-04-20 | rev 11 | Francesca Palombini | history.html:1463

[Ballot Position Update] New position, No Objection, has been recorded for Francesca Palombini

## history-803785 | 2021-04-19 | rev 11 | Alvaro Retana | history.html:1472

[Ballot Position Update] New position, No Objection, has been recorded for Alvaro Retana

## history-803748 | 2021-04-19 | rev 11 | Martin Vigoureux | history.html:1481

[Ballot Position Update] New position, No Objection, has been recorded for Martin Vigoureux

## history-803700 | 2021-04-19 | rev 11 | Robert Wilton | history.html:1490

[Ballot comment]
Hi,

I'm no DTLS expert, but I found the concepts/explanation in this document easy to follow.

I was slightly confused by the requirement to encode the length in variable length CIDs, and had to read the relevant text a second time. As a suggestion, it might help if these two sentences were reworded the other way round:

OLD:
Implementations that want to use
 variable-length CIDs are responsible for constructing the CID in such
 a way that its length can be determined on reception. Note that
 there is no CID length information included in the record itself.

NEW:
Since the CID length information is not included in the record itself, implementations that want to use ... .

One minor question. In the contributors, I noted that Jana is listed as being associated with Google, but it might be worth checking if that is still accurate.

Regards.
Rob

## history-803699 | 2021-04-19 | rev 11 | Robert Wilton | history.html:1499

[Ballot Position Update] New position, No Objection, has been recorded for Robert Wilton

## history-803691 | 2021-04-19 | rev 11 | Éric Vyncke | history.html:1508

[Ballot comment]
Thank you for the work put into this document. This specification addresses the IPv4-mainly issue of NAT binding and is still required. I am also trusted the security ADs for section 5.

Please find below some non-blocking COMMENT points (but replies would be appreciated), and some nits.

I hope that this helps to improve the document,

Regards,

-éric

== COMMENTS ==

-- Abstract --
As an important part of this document is the padding, should it be mentioned also in the abstract ?

-- Section 3 --
While I am not a DTLS expert, I find this section quite difficult to understand the reasoning behind the specification as little explanations are given about, e.g, what is the motivation of "A zero-length value indicates that the server will send with the client's CID but does not wish the client to include a CID."

-- Section 6 --
I am puzzled by the text:
 "There is a strategy for ensuring that the new peer address is able
 to receive and process DTLS records. No such strategy is defined
 in this specification."
Does this mean that there is no way to update the peer IP address ?

== NITS ==

-- Section 1 --
Please expand CID on first use outside of the abstract.

-- Section 4 --
Suggest to add a short paragraph as a preamble to figure 3. Currently, it looks like figure 3 belongs to the 'zeros' field description.

## history-803690 | 2021-04-19 | rev 11 | Éric Vyncke | history.html:1517

[Ballot Position Update] New position, No Objection, has been recorded for Éric Vyncke

## history-803525 | 2021-04-16 | rev 11 | Amanda Baber | history.html:1526

IANA Review state changed to IANA OK - Actions Needed from Version Changed - Review Needed

## history-803217 | 2021-04-15 | rev 11 | Amy Vezza | history.html:1535

Placed on agenda for telechat - 2021-04-22

## history-803102 | 2021-04-14 | rev 11 | Benjamin Kaduk | history.html:1544

Ballot has been issued

## history-803101 | 2021-04-14 | rev 11 | Benjamin Kaduk | history.html:1553

[Ballot Position Update] New position, Yes, has been recorded for Benjamin Kaduk

## history-803100 | 2021-04-14 | rev 11 | Benjamin Kaduk | history.html:1562

Created "Approve" ballot

## history-803099 | 2021-04-14 | rev 11 | (System) | history.html:1571

Changed action holders to Benjamin Kaduk (IESG state changed)

## history-803098 | 2021-04-14 | rev 11 | Benjamin Kaduk | history.html:1580

IESG state changed to IESG Evaluation from Waiting for Writeup::AD Followup

## history-803097 | 2021-04-14 | rev 11 | Benjamin Kaduk | history.html:1589

Ballot writeup was changed

## history-803007 | 2021-04-14 | rev 11 | (System) | history.html:1598

Sub state has been changed to AD Followup from Revised ID Needed

## history-803006 | 2021-04-14 | rev 11 | (System) | history.html:1607

IANA Review state changed to Version Changed - Review Needed from IANA - Not OK

## history-803005 | 2021-04-14 | rev 11 | Eric Rescorla | history.html:1616

New version available: draft-ietf-tls-dtls-connection-id-11.txt

## history-803004 | 2021-04-14 | rev 11 | (System) | history.html:1625

New version approved

## history-803003 | 2021-04-14 | rev 11 | (System) | history.html:1634

Request for posting confirmation emailed to previous authors: Achim Kraus , Eric Rescorla , Hannes Tschofenig , Thomas Fossati

## history-803002 | 2021-04-14 | rev 11 | Eric Rescorla | history.html:1643

Uploaded new revision

## history-802912 | 2021-04-13 | rev 10 | (System) | history.html:1652

Changed action holders to Eric Rescorla, Hannes Tschofenig, Thomas Fossati, Benjamin Kaduk, Achim Kraus (IESG state changed)

## history-802911 | 2021-04-13 | rev 10 | Benjamin Kaduk | history.html:1661

IESG state changed to Waiting for Writeup::Revised I-D Needed from Waiting for Writeup

## history-801041 | 2021-03-30 | rev 10 | Magnus Westerlund | history.html:1670

Request closed, assignment withdrawn: Jana Iyengar Last Call TSVART review

## history-801040 | 2021-03-30 | rev 10 | Magnus Westerlund | history.html:1679

Closed request for Last Call review by TSVART with state 'Overtaken by Events'

## history-800778 | 2021-03-28 | rev 10 | (System) | history.html:1688

IESG state changed to Waiting for Writeup from In Last Call

## history-800703 | 2021-03-26 | rev 10 | Sabrina Tanamal | history.html:1697

IANA Experts State changed to Expert Reviews OK from Reviews assigned

## history-800639 | 2021-03-26 | rev 10 | Sabrina Tanamal | history.html:1706

IANA Experts State changed to Reviews assigned

## history-800656 | 2021-03-26 | rev 10 | (System) | history.html:1715

IANA Review state changed to IANA - Not OK from IANA - Review Needed

## history-800636 | 2021-03-26 | rev 10 | Sabrina Tanamal | history.html:1724

(Via drafts-lastcall@iana.org): IESG/Authors/WG Chairs:

The IANA Functions Operator has completed its review of draft-ietf-tls-dtls-connection-id-10. If any part of this review is inaccurate, please let us know. 

The IANA Functions Operator has a question about one of the actions requested in the IANA Considerations section of this document.

The IANA Functions Operator understands that, upon approval of this document, there are three actions which we must complete.

First, in the TLS ExtensionType Values registry on the Transport Layer Security (TLS) Extensions registry page located at:

https://www.iana.org/assignments/tls-extensiontype-values/

a new column - "DTLS Only?" - will be added to the registry and [ RFC-to-be ] will be added as an additional reference for the registry.

IANA Question --> What are the entries for DTLS Only? for the existing registrations in the current registry?

Second, also in the TLS ExtensionType Values registry on the Transport Layer Security (TLS) Extensions registry page located at:

https://www.iana.org/assignments/tls-extensiontype-values/

the temporary registration for value 53 connection_id will be updated as follows:

Value: 53
Extension Name: connection_id
TLS 1.3: CH, SH
DTLS Only: Y
Recommended: N
Reference: [ RFC-to-be ]

Since the TLS 1.3 column has been updated, we're asking the TLS ExtensionType Value experts to review and approve. This review must be completed before the document's IANA state can be changed to "IANA OK."

Third, in the TLS ContentType registry on the Transport Layer Security (TLS) Parameters registry page located at:

https://www.iana.org/assignments/tls-parameters/

the temporary registration for value 25 (tls12_cid) will be made permanent and the reference will be changed to [ RFC-to-be ].

The IANA Functions Operator understands that these are the only actions required to be completed upon approval of this document.

Note: The actions requested in this document will not be completed until the document has been approved for publication as an RFC. This message is meant only to confirm the list of actions that will be performed. 

Thank you,

Sabrina Tanamal
Senior IANA Services Specialist

## history-799594 | 2021-03-19 | rev 10 | Gunter Van de Velde | history.html:1733

Request for Last Call review by OPSDIR is assigned to Jon Mitchell

## history-799593 | 2021-03-19 | rev 10 | Gunter Van de Velde | history.html:1742

Request for Last Call review by OPSDIR is assigned to Jon Mitchell

## history-799167 | 2021-03-15 | rev 10 | Russ Housley | history.html:1751

Request for Last Call review by GENART Completed: Ready. Reviewer: Russ Housley. Sent review to list.

## history-798864 | 2021-03-12 | rev 10 | Jean Mahoney | history.html:1760

Request for Last Call review by GENART is assigned to Russ Housley

## history-798863 | 2021-03-12 | rev 10 | Jean Mahoney | history.html:1769

Request for Last Call review by GENART is assigned to Russ Housley

## history-798398 | 2021-03-11 | rev 10 | Tero Kivinen | history.html:1778

Request for Last Call review by SECDIR is assigned to Daniel Franke

## history-798397 | 2021-03-11 | rev 10 | Tero Kivinen | history.html:1787

Request for Last Call review by SECDIR is assigned to Daniel Franke

## history-797522 | 2021-03-09 | rev 10 | Magnus Westerlund | history.html:1796

Request for Last Call review by TSVART is assigned to Jana Iyengar

## history-797521 | 2021-03-09 | rev 10 | Magnus Westerlund | history.html:1805

Request for Last Call review by TSVART is assigned to Jana Iyengar

## history-796683 | 2021-03-08 | rev 10 | Cindy Morgan | history.html:1814

IANA Review state changed to IANA - Review Needed

## history-796682 | 2021-03-08 | rev 10 | Cindy Morgan | history.html:1823

The following Last Call announcement was sent out (ends 2021-03-28):

From: The IESG 
To: IETF-Announce 
CC: Joseph Salowey , draft-ietf-tls-dtls-connection-id@ietf.org, joe@salowey.net, kaduk@mit.edu, tls-chairs@ietf.org, tls@ietf.org
Reply-To: last-call@ietf.org
Sender: 
Subject: Last Call: (Connection Identifiers for DTLS 1.2) to Proposed Standard


The IESG has received a request from the Transport Layer Security WG (tls) to
consider the following document: - 'Connection Identifiers for DTLS 1.2'
 as Proposed Standard

The IESG plans to make a decision in the next few weeks, and solicits final
comments on this action. Please send substantive comments to the
last-call@ietf.org mailing lists by 2021-03-28. Exceptionally, comments may
be sent to iesg@ietf.org instead. In either case, please retain the beginning
of the Subject line to allow automated sorting.

Abstract


 This document specifies the Connection ID (CID) construct for the
 Datagram Transport Layer Security (DTLS) protocol version 1.2.

 A CID is an identifier carried in the record layer header that gives
 the recipient additional information for selecting the appropriate
 security association. In "classical" DTLS, selecting a security
 association of an incoming DTLS record is accomplished with the help
 of the 5-tuple. If the source IP address and/or source port changes
 during the lifetime of an ongoing DTLS session then the receiver will
 be unable to locate the correct security context.




The file can be obtained via
https://datatracker.ietf.org/doc/draft-ietf-tls-dtls-connection-id/



No IPR declarations have been submitted directly on this I-D.

## history-796681 | 2021-03-08 | rev 10 | Cindy Morgan | history.html:1832

IESG state changed to In Last Call from Last Call Requested

## history-796423 | 2021-03-07 | rev 10 | Benjamin Kaduk | history.html:1841

Last call was requested

## history-796422 | 2021-03-07 | rev 10 | Benjamin Kaduk | history.html:1850

Ballot approval text was generated

## history-796421 | 2021-03-07 | rev 10 | Benjamin Kaduk | history.html:1859

Ballot writeup was generated

## history-796420 | 2021-03-07 | rev 10 | (System) | history.html:1868

Changed action holders to Benjamin Kaduk (IESG state changed)

## history-796419 | 2021-03-07 | rev 10 | Benjamin Kaduk | history.html:1877

IESG state changed to Last Call Requested from AD Evaluation::AD Followup

## history-796418 | 2021-03-07 | rev 10 | Benjamin Kaduk | history.html:1886

Last call announcement was changed

## history-796417 | 2021-03-07 | rev 10 | Benjamin Kaduk | history.html:1895

Last call announcement was generated

## history-796399 | 2021-03-07 | rev 10 | (System) | history.html:1904

Sub state has been changed to AD Followup from Revised ID Needed

## history-796398 | 2021-03-07 | rev 10 | Eric Rescorla | history.html:1913

New version available: draft-ietf-tls-dtls-connection-id-10.txt

## history-796397 | 2021-03-07 | rev 10 | (System) | history.html:1922

New version approved

## history-796396 | 2021-03-07 | rev 10 | (System) | history.html:1931

Request for posting confirmation emailed to previous authors: Eric Rescorla , Hannes Tschofenig , Thomas Fossati , tls-chairs@ietf.org

## history-796395 | 2021-03-07 | rev 10 | Eric Rescorla | history.html:1940

Uploaded new revision

## history-795284 | 2021-02-27 | rev 09 | Benjamin Kaduk | history.html:1949

A few pull requests have landed, so let's publish them as an I-D (once the submissions block is lifted) and start the IETF LC.

## history-795283 | 2021-02-27 | rev 09 | (System) | history.html:1958

Changed action holders to Eric Rescorla, Hannes Tschofenig, Thomas Fossati (IESG state changed)

## history-795282 | 2021-02-27 | rev 09 | Benjamin Kaduk | history.html:1967

IESG state changed to AD Evaluation::Revised I-D Needed from AD Evaluation::AD Followup

## history-787472 | 2021-01-17 | rev 09 | (System) | history.html:1976

Sub state has been changed to AD Followup from Revised ID Needed

## history-787471 | 2021-01-17 | rev 09 | Hannes Tschofenig | history.html:1985

New version available: draft-ietf-tls-dtls-connection-id-09.txt

## history-787470 | 2021-01-17 | rev 09 | (System) | history.html:1994

New version approved

## history-787469 | 2021-01-17 | rev 09 | (System) | history.html:2003

Request for posting confirmation emailed to previous authors: Eric Rescorla , Hannes Tschofenig , Thomas Fossati

## history-787468 | 2021-01-17 | rev 09 | Hannes Tschofenig | history.html:2012

Uploaded new revision

## history-785181 | 2020-12-29 | rev 08 | Benjamin Kaduk | history.html:2021

Some good changes have landed in git at https://github.com/tlswg/dtls-conn-id but are not in the I-D repository yet.

## history-785180 | 2020-12-29 | rev 08 | Benjamin Kaduk | history.html:2030

IESG state changed to AD Evaluation::Revised I-D Needed from AD Evaluation::AD Followup

## history-779719 | 2020-11-16 | rev 08 | Sean Turner | history.html:2039

Added to session: IETF-109: tls Tue-1430

## history-776973 | 2020-11-02 | rev 08 | (System) | history.html:2048

Sub state has been changed to AD Followup from Revised ID Needed

## history-776972 | 2020-11-02 | rev 08 | Hannes Tschofenig | history.html:2057

New version available: draft-ietf-tls-dtls-connection-id-08.txt

## history-776971 | 2020-11-02 | rev 08 | (System) | history.html:2066

New version accepted (logged-in submitter: Hannes Tschofenig)

## history-776970 | 2020-11-02 | rev 08 | Hannes Tschofenig | history.html:2075

Uploaded new revision

## history-769659 | 2020-09-15 | rev 07 | Benjamin Kaduk | history.html:2084

IESG state changed to AD Evaluation::Revised I-D Needed from AD Evaluation

## history-761841 | 2020-07-26 | rev 07 | Benjamin Kaduk | history.html:2093

IESG state changed to AD Evaluation from Publication Requested

## history-720243 | 2019-11-21 | rev 07 | Joseph Salowey | history.html:2102

As required by RFC 4858, this is the current template for the Document 
Shepherd Write-Up.

Changes are expected over time. This version is dated 24 February 2012.

(1) What type of RFC is being requested (BCP, Proposed Standard,
Internet Standard, Informational, Experimental, or Historic)? Why
is this the proper type of RFC? Is this type of RFC indicated in the
title page header?

The proposed Status of the document is Proposed Standard.

(2) The IESG approval announcement includes a Document Announcement
Write-Up. Please provide such a Document Announcement Write-Up. Recent
examples can be found in the "Action" announcements for approved
documents. The approval announcement contains the following sections:

Technical Summary

 This document specifies the Connection ID (CID) construct for the
 Datagram Transport Layer Security (DTLS) protocol version 1.2.

 A CID is an identifier carried in the record layer header that gives
 the recipient additional information for selecting the appropriate
 security association. In "classical" DTLS, selecting a security
 association of an incoming DTLS record is accomplished with the help
 of the 5-tuple. If the source IP address and/or source port changes
 during the lifetime of an ongoing DTLS session then the receiver will
 be unable to locate the correct security context.

Working Group Summary

 Was there anything in WG process that is worth noting? For 
 example, was there controversy about particular points or 
 were there decisions where the consensus was particularly 
 rough?

The document is of interest to a subset of the working group 
participants. The participants are active and there is general 
working group consensus behind the document. 

Document Quality

The document has been reviewed by people implementing 
 the protocol. There are multiple implementations of this 
extension.

Personnel

The Document Shepherd is Joseph Salowey and the responsible AD is Ben Kaduk

(3) Briefly describe the review of this document that was performed by
the Document Shepherd. If this version of the document is not ready
for publication, please explain why the document is being forwarded to
the IESG.

The shepherd has reviewed the document and believes it is ready for publication. 
The reference to the obsoleted TLS version is intentional. 
The document needs to have a reference to RFC 6347 added to the abstract as it
only mentions the document by name. 

(4) Does the document Shepherd have any concerns about the depth or
breadth of the reviews that have been performed?

No

(5) Do portions of the document need review from a particular or from
broader perspective, e.g., security, operational complexity, AAA, DNS,
DHCP, XML, or internationalization? If so, describe the review that
took place.

No

(6) Describe any specific concerns or issues that the Document Shepherd
has with this document that the Responsible Area Director and/or the
IESG should be aware of? For example, perhaps he or she is uncomfortable
with certain parts of the document, or has concerns whether there really
is a need for it. In any event, if the WG has discussed those issues and
has indicated that it still wishes to advance the document, detail those
concerns here.

No Specific Concerns

(7) Has each author confirmed that any and all appropriate IPR
disclosures required for full conformance with the provisions of BCP 78
and BCP 79 have already been filed. If not, explain why.

The authors have confirmed conformance with BCP 78 and BCP 79.

(8) Has an IPR disclosure been filed that references this document?
If so, summarize any WG discussion and conclusion regarding the IPR
disclosures.

No declared IPR

(9) How solid is the WG consensus behind this document? Does it 
represent the strong concurrence of a few individuals, with others
being silent, or does the WG as a whole understand and agree with it? 

The document has been worked on by a subset of the TLS community.
The document has had review from participants outside this 
subset and there is general consensus behind this document. 

(10) Has anyone threatened an appeal or otherwise indicated extreme 
discontent? If so, please summarise the areas of conflict in separate
email messages to the Responsible Area Director. (It should be in a
separate email because this questionnaire is publicly available.) 

NA

(11) Identify any ID nits the Document Shepherd has found in this
document. (See https://www.ietf.org/tools/idnits/ and the Internet-Drafts
Checklist). Boilerplate checks are not enough; this check needs to be
thorough.

No Nits

(12) Describe how the document meets any required formal review
criteria, such as the MIB Doctor, media type, and URI type reviews.

NA

(13) Have all references within this document been identified as
either normative or informative?

Yes

(14) Are there normative references to documents that are not ready for
advancement or are otherwise in an unclear state? If such normative
references exist, what is the plan for their completion?

No

(15) Are there downward normative references references (see RFC 3967)?
If so, list these downward references to support the Area Director in 
the Last Call procedure. 

No

(16) Will publication of this document change the status of any
existing RFCs? Are those RFCs listed on the title page header, listed
in the abstract, and discussed in the introduction? If the RFCs are not
listed in the Abstract and Introduction, explain why, and point to the
part of the document where the relationship of this document to the
other RFCs is discussed. If this information is not in the document,
explain why the WG considers it unnecessary.

This document updates RFC 6347 (DTLS 1.2). The abstract mentions DTLS 1.2
but does not include the RFC number reference. This can be easily fixed 
later in the process

(17) Describe the Document Shepherd's review of the IANA considerations
section, especially with regard to its consistency with the body of the
document. Confirm that all protocol extensions that the document makes
are associated with the appropriate reservations in IANA registries.
Confirm that any referenced IANA registries have been clearly
identified. Confirm that newly created IANA registries include a
detailed specification of the initial contents for the registry, that
allocations procedures for future registrations are defined, and a
reasonable name for the new registry has been suggested (see RFC 8126).

The IANA considerations registers an entry for the extension and content 
type associated with this document 

(18) List any new IANA registries that require Expert Review for future
allocations. Provide any public guidance that the IESG would find
useful in selecting the IANA Experts for these new registries.

No new registries. 

(19) Describe reviews and automated checks performed by the Document
Shepherd to validate sections of the document written in a formal
language, such as XML code, BNF rules, MIB definitions, etc.

NA

## history-720242 | 2019-11-21 | rev 07 | Joseph Salowey | history.html:2111

Responsible AD changed to Benjamin Kaduk

## history-720241 | 2019-11-21 | rev 07 | Joseph Salowey | history.html:2120

IETF WG state changed to Submitted to IESG for Publication from WG Consensus: Waiting for Write-Up

## history-720240 | 2019-11-21 | rev 07 | Joseph Salowey | history.html:2129

IESG state changed to Publication Requested from I-D Exists

## history-720239 | 2019-11-21 | rev 07 | Joseph Salowey | history.html:2138

IESG process started in state Publication Requested

## history-719920 | 2019-11-20 | rev 07 | Joseph Salowey | history.html:2147

Tag Doc Shepherd Follow-up Underway cleared.

## history-719919 | 2019-11-20 | rev 07 | Joseph Salowey | history.html:2156

IETF WG state changed to WG Consensus: Waiting for Write-Up from Waiting for WG Chair Go-Ahead

## history-719779 | 2019-11-20 | rev 07 | Joseph Salowey | history.html:2165

As required by RFC 4858, this is the current template for the Document 
Shepherd Write-Up.

Changes are expected over time. This version is dated 24 February 2012.

(1) What type of RFC is being requested (BCP, Proposed Standard,
Internet Standard, Informational, Experimental, or Historic)? Why
is this the proper type of RFC? Is this type of RFC indicated in the
title page header?

The proposed Status of the document is Proposed Standard.

(2) The IESG approval announcement includes a Document Announcement
Write-Up. Please provide such a Document Announcement Write-Up. Recent
examples can be found in the "Action" announcements for approved
documents. The approval announcement contains the following sections:

Technical Summary

 This document specifies the Connection ID (CID) construct for the
 Datagram Transport Layer Security (DTLS) protocol version 1.2.

 A CID is an identifier carried in the record layer header that gives
 the recipient additional information for selecting the appropriate
 security association. In "classical" DTLS, selecting a security
 association of an incoming DTLS record is accomplished with the help
 of the 5-tuple. If the source IP address and/or source port changes
 during the lifetime of an ongoing DTLS session then the receiver will
 be unable to locate the correct security context.

Working Group Summary

 Was there anything in WG process that is worth noting? For 
 example, was there controversy about particular points or 
 were there decisions where the consensus was particularly 
 rough?

The document is of interest to a subset of the working group 
participants. The participants are active and there is general 
working group consensus behind the document. 

Document Quality

The document has been reviewed by people implementing 
 the protocol. There are multiple implementations of this 
extension.

Personnel

The Document Shepherd is Joseph Salowey and the responsible AD is Ben Kaduk

(3) Briefly describe the review of this document that was performed by
the Document Shepherd. If this version of the document is not ready
for publication, please explain why the document is being forwarded to
the IESG.

The shepherd has reviewed the document and believes it is ready for publication. 
The reference to the obsoleted TLS version is intentional. 
The document needs to have a reference to RFC 6347 added to the abstract as it
only mentions the document by name. 

(4) Does the document Shepherd have any concerns about the depth or
breadth of the reviews that have been performed?

No

(5) Do portions of the document need review from a particular or from
broader perspective, e.g., security, operational complexity, AAA, DNS,
DHCP, XML, or internationalization? If so, describe the review that
took place.

No

(6) Describe any specific concerns or issues that the Document Shepherd
has with this document that the Responsible Area Director and/or the
IESG should be aware of? For example, perhaps he or she is uncomfortable
with certain parts of the document, or has concerns whether there really
is a need for it. In any event, if the WG has discussed those issues and
has indicated that it still wishes to advance the document, detail those
concerns here.

No Specific Concerns

(7) Has each author confirmed that any and all appropriate IPR
disclosures required for full conformance with the provisions of BCP 78
and BCP 79 have already been filed. If not, explain why.

The authors have confirmed conformance with BCP 78 and BCP 79.

(8) Has an IPR disclosure been filed that references this document?
If so, summarize any WG discussion and conclusion regarding the IPR
disclosures.

No declared IPR

(9) How solid is the WG consensus behind this document? Does it 
represent the strong concurrence of a few individuals, with others
being silent, or does the WG as a whole understand and agree with it? 

The document has been worked on by a subset of the TLS community.
The document has had review from participants outside this 
subset and there is general consensus behind this document. 

(10) Has anyone threatened an appeal or otherwise indicated extreme 
discontent? If so, please summarise the areas of conflict in separate
email messages to the Responsible Area Director. (It should be in a
separate email because this questionnaire is publicly available.) 

NA

(11) Identify any ID nits the Document Shepherd has found in this
document. (See https://www.ietf.org/tools/idnits/ and the Internet-Drafts
Checklist). Boilerplate checks are not enough; this check needs to be
thorough.

No Nits

(12) Describe how the document meets any required formal review
criteria, such as the MIB Doctor, media type, and URI type reviews.

NA

(13) Have all references within this document been identified as
either normative or informative?

Yes

(14) Are there normative references to documents that are not ready for
advancement or are otherwise in an unclear state? If such normative
references exist, what is the plan for their completion?

No

(15) Are there downward normative references references (see RFC 3967)?
If so, list these downward references to support the Area Director in 
the Last Call procedure. 

No

(16) Will publication of this document change the status of any
existing RFCs? Are those RFCs listed on the title page header, listed
in the abstract, and discussed in the introduction? If the RFCs are not
listed in the Abstract and Introduction, explain why, and point to the
part of the document where the relationship of this document to the
other RFCs is discussed. If this information is not in the document,
explain why the WG considers it unnecessary.

This document updates RFC 6347 (DTLS 1.2). The abstract mentions DTLS 1.2
but does not include the RFC number reference. This can be easily fixed 
later in the process

(17) Describe the Document Shepherd's review of the IANA considerations
section, especially with regard to its consistency with the body of the
document. Confirm that all protocol extensions that the document makes
are associated with the appropriate reservations in IANA registries.
Confirm that any referenced IANA registries have been clearly
identified. Confirm that newly created IANA registries include a
detailed specification of the initial contents for the registry, that
allocations procedures for future registrations are defined, and a
reasonable name for the new registry has been suggested (see RFC 8126).

The IANA considerations registers an entry for the extension and content 
type associated with this document 

(18) List any new IANA registries that require Expert Review for future
allocations. Provide any public guidance that the IESG would find
useful in selecting the IANA Experts for these new registries.

No new registries. 

(19) Describe reviews and automated checks performed by the Document
Shepherd to validate sections of the document written in a formal
language, such as XML code, BNF rules, MIB definitions, etc.

NA

## history-719046 | 2019-11-19 | rev 07 | Joseph Salowey | history.html:2174

Tag Doc Shepherd Follow-up Underway set. Tag Revised I-D Needed - Issue raised by WGLC cleared.

## history-715408 | 2019-11-04 | rev 07 | Sean Turner | history.html:2183

Changed document URLs from:

[]

to:

repository https://github.com/tlswg/dtls-conn-id

## history-711847 | 2019-10-21 | rev 07 | Hannes Tschofenig | history.html:2192

New version available: draft-ietf-tls-dtls-connection-id-07.txt

## history-711846 | 2019-10-21 | rev 07 | (System) | history.html:2201

New version approved

## history-711845 | 2019-10-21 | rev 07 | (System) | history.html:2210

Request for posting confirmation emailed to previous authors: Hannes Tschofenig , Eric Rescorla , Thomas Fossati

## history-711844 | 2019-10-21 | rev 07 | Hannes Tschofenig | history.html:2219

Uploaded new revision

## history-694437 | 2019-07-08 | rev 06 | Thomas Fossati | history.html:2228

New version available: draft-ietf-tls-dtls-connection-id-06.txt

## history-694436 | 2019-07-08 | rev 06 | (System) | history.html:2237

New version approved

## history-694435 | 2019-07-08 | rev 06 | (System) | history.html:2246

Request for posting confirmation emailed to previous authors: Hannes Tschofenig , Eric Rescorla , Thomas Fossati

## history-694434 | 2019-07-08 | rev 06 | Thomas Fossati | history.html:2255

Uploaded new revision

## history-689758 | 2019-06-13 | rev 05 | Joseph Salowey | history.html:2264

As required by RFC 4858, this is the current template for the Document 
Shepherd Write-Up.

Changes are expected over time. This version is dated 24 February 2012.

(1) What type of RFC is being requested (BCP, Proposed Standard,
Internet Standard, Informational, Experimental, or Historic)? Why
is this the proper type of RFC? Is this type of RFC indicated in the
title page header?

The proposed Status of the document is Proposed Standard.

(2) The IESG approval announcement includes a Document Announcement
Write-Up. Please provide such a Document Announcement Write-Up. Recent
examples can be found in the "Action" announcements for approved
documents. The approval announcement contains the following sections:

Technical Summary

 This document specifies the Connection ID (CID) construct for the
 Datagram Transport Layer Security (DTLS) protocol version 1.2.

 A CID is an identifier carried in the record layer header that gives
 the recipient additional information for selecting the appropriate
 security association. In "classical" DTLS, selecting a security
 association of an incoming DTLS record is accomplished with the help
 of the 5-tuple. If the source IP address and/or source port changes
 during the lifetime of an ongoing DTLS session then the receiver will
 be unable to locate the correct security context.

Working Group Summary

 Was there anything in WG process that is worth noting? For 
 example, was there controversy about particular points or 
 were there decisions where the consensus was particularly 
 rough?

The document is of interest to a subset of the working group 
participants. The participants are active and there is general 
working group consensus behind the document. 

Document Quality

The document has been reviewed by people implementing 
 the protocol

Personnel

The Document Shepherd is Joseph Salowey and the responsible AD is Ben Kaduk

(3) Briefly describe the review of this document that was performed by
the Document Shepherd. If this version of the document is not ready
for publication, please explain why the document is being forwarded to
the IESG.

The shepherd has reviewed the document and believes it is ready for publication.

(4) Does the document Shepherd have any concerns about the depth or
breadth of the reviews that have been performed?

No

(5) Do portions of the document need review from a particular or from
broader perspective, e.g., security, operational complexity, AAA, DNS,
DHCP, XML, or internationalization? If so, describe the review that
took place.

No

(6) Describe any specific concerns or issues that the Document Shepherd
has with this document that the Responsible Area Director and/or the
IESG should be aware of? For example, perhaps he or she is uncomfortable
with certain parts of the document, or has concerns whether there really
is a need for it. In any event, if the WG has discussed those issues and
has indicated that it still wishes to advance the document, detail those
concerns here.

No Specific Concerns

(7) Has each author confirmed that any and all appropriate IPR
disclosures required for full conformance with the provisions of BCP 78
and BCP 79 have already been filed. If not, explain why.

Check in progress

(8) Has an IPR disclosure been filed that references this document?
If so, summarize any WG discussion and conclusion regarding the IPR
disclosures.

No declared IPR

(9) How solid is the WG consensus behind this document? Does it 
represent the strong concurrence of a few individuals, with others
being silent, or does the WG as a whole understand and agree with it? 

The document has been worked on by a subset of the TLS community,
but the document has had review from participants outside this 
subset and there is general consensus behind this document. 

(10) Has anyone threatened an appeal or otherwise indicated extreme 
discontent? If so, please summarise the areas of conflict in separate
email messages to the Responsible Area Director. (It should be in a
separate email because this questionnaire is publicly available.) 

NA

(11) Identify any ID nits the Document Shepherd has found in this
document. (See https://www.ietf.org/tools/idnits/ and the Internet-Drafts
Checklist). Boilerplate checks are not enough; this check needs to be
thorough.

No Nits

(12) Describe how the document meets any required formal review
criteria, such as the MIB Doctor, media type, and URI type reviews.

NA

(13) Have all references within this document been identified as
either normative or informative?

Yes

(14) Are there normative references to documents that are not ready for
advancement or are otherwise in an unclear state? If such normative
references exist, what is the plan for their completion?

No

(15) Are there downward normative references references (see RFC 3967)?
If so, list these downward references to support the Area Director in 
the Last Call procedure. 

No

(16) Will publication of this document change the status of any
existing RFCs? Are those RFCs listed on the title page header, listed
in the abstract, and discussed in the introduction? If the RFCs are not
listed in the Abstract and Introduction, explain why, and point to the
part of the document where the relationship of this document to the
other RFCs is discussed. If this information is not in the document,
explain why the WG considers it unnecessary.

TBD

(17) Describe the Document Shepherd's review of the IANA considerations
section, especially with regard to its consistency with the body of the
document. Confirm that all protocol extensions that the document makes
are associated with the appropriate reservations in IANA registries.
Confirm that any referenced IANA registries have been clearly
identified. Confirm that newly created IANA registries include a
detailed specification of the initial contents for the registry, that
allocations procedures for future registrations are defined, and a
reasonable name for the new registry has been suggested (see RFC 8126).

In Porgress

(18) List any new IANA registries that require Expert Review for future
allocations. Provide any public guidance that the IESG would find
useful in selecting the IANA Experts for these new registries.

No new registries. 

(19) Describe reviews and automated checks performed by the Document
Shepherd to validate sections of the document written in a formal
language, such as XML code, BNF rules, MIB definitions, etc.

NA

## history-664797 | 2019-05-06 | rev 05 | Hannes Tschofenig | history.html:2273

New version available: draft-ietf-tls-dtls-connection-id-05.txt

## history-664796 | 2019-05-06 | rev 05 | (System) | history.html:2282

New version approved

## history-664793 | 2019-05-06 | rev 05 | (System) | history.html:2291

Request for posting confirmation emailed to previous authors: Hannes Tschofenig , Eric Rescorla , Thomas Fossati

## history-664792 | 2019-05-06 | rev 05 | Hannes Tschofenig | history.html:2300

Uploaded new revision

## history-653789 | 2019-03-11 | rev 04 | Hannes Tschofenig | history.html:2309

New version available: draft-ietf-tls-dtls-connection-id-04.txt

## history-653788 | 2019-03-11 | rev 04 | (System) | history.html:2318

New version approved

## history-653787 | 2019-03-11 | rev 04 | (System) | history.html:2327

Request for posting confirmation emailed to previous authors: Hannes Tschofenig , Eric Rescorla , Thomas Fossati

## history-653786 | 2019-03-11 | rev 04 | Hannes Tschofenig | history.html:2336

Uploaded new revision

## history-650913 | 2019-02-27 | rev 03 | Hannes Tschofenig | history.html:2345

New version available: draft-ietf-tls-dtls-connection-id-03.txt

## history-650912 | 2019-02-27 | rev 03 | (System) | history.html:2354

New version approved

## history-650911 | 2019-02-27 | rev 03 | (System) | history.html:2363

Request for posting confirmation emailed to previous authors: Eric Rescorla , Hannes Tschofenig , Thomas Fossati , Tobias Gondrom , tls-chairs@ietf.org

## history-650910 | 2019-02-27 | rev 03 | Hannes Tschofenig | history.html:2372

Uploaded new revision

## history-640731 | 2018-12-10 | rev 02 | Joseph Salowey | history.html:2381

Tag Revised I-D Needed - Issue raised by WGLC set.

## history-640730 | 2018-12-10 | rev 02 | Joseph Salowey | history.html:2390

IETF WG state changed to Waiting for WG Chair Go-Ahead from In WG Last Call

## history-636332 | 2018-11-06 | rev 02 | Joseph Salowey | history.html:2399

IETF WG state changed to In WG Last Call from WG Document

## history-635810 | 2018-11-05 | rev 02 | Sean Turner | history.html:2408

Notification list changed to Joseph Salowey <joe@salowey.net>

## history-635809 | 2018-11-05 | rev 02 | Sean Turner | history.html:2417

Document shepherd changed to Joseph A. Salowey

## history-635807 | 2018-11-05 | rev 02 | Sean Turner | history.html:2426

Changed consensus to Yes from Unknown

## history-635806 | 2018-11-05 | rev 02 | Sean Turner | history.html:2435

Intended Status changed to Proposed Standard from None

## history-633688 | 2018-10-31 | rev 02 | Sean Turner | history.html:2444

Added to session: IETF-103: tls Mon-1350

## history-632044 | 2018-10-22 | rev 02 | Eric Rescorla | history.html:2453

New version available: draft-ietf-tls-dtls-connection-id-02.txt

## history-632043 | 2018-10-22 | rev 02 | (System) | history.html:2462

New version approved

## history-632042 | 2018-10-22 | rev 02 | (System) | history.html:2471

Request for posting confirmation emailed to previous authors: Eric Rescorla , Hannes Tschofenig , Thomas Fossati , Tobias Gondrom

## history-632041 | 2018-10-22 | rev 02 | Eric Rescorla | history.html:2480

Uploaded new revision

## history-613125 | 2018-07-02 | rev 01 | Eric Rescorla | history.html:2489

New version available: draft-ietf-tls-dtls-connection-id-01.txt

## history-613124 | 2018-07-02 | rev 01 | (System) | history.html:2498

New version approved

## history-613123 | 2018-07-02 | rev 01 | (System) | history.html:2507

Request for posting confirmation emailed to previous authors: Eric Rescorla , Hannes Tschofenig , Thomas Fossati , Tobias Gondrom

## history-613122 | 2018-07-02 | rev 01 | Eric Rescorla | history.html:2516

Uploaded new revision

## history-613121 | 2018-07-02 | rev 01 | Eric Rescorla | history.html:2525

Uploaded new revision

## history-612356 | 2018-06-30 | rev 00 | (System) | history.html:2534

Document has expired

## history-580135 | 2018-01-04 | rev 00 | Sean Turner | history.html:2543

This document now replaces draft-rescorla-tls-dtls-connection-id instead of None

## history-579125 | 2017-12-27 | rev 00 | Eric Rescorla | history.html:2552

New version available: draft-ietf-tls-dtls-connection-id-00.txt

## history-579124 | 2017-12-27 | rev 00 | (System) | history.html:2561

New version approved

## history-579123 | 2017-12-27 | rev 00 | Eric Rescorla | history.html:2570

Request for posting confirmation emailed to submitter and authors: Eric Rescorla , Hannes Tschofenig , Thomas Fossati , Tobias Gondrom

## history-579122 | 2017-12-27 | rev 00 | Eric Rescorla | history.html:2579

Uploaded new revision
