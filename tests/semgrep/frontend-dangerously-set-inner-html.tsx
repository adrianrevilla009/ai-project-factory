// ruleid: frontend-dangerously-set-inner-html-unsanitized
export const A = ({ html }: { html: string }) => <div dangerouslySetInnerHTML={{ __html: html }} />;
// ok: frontend-dangerously-set-inner-html-unsanitized
export const B = ({ html }: { html: string }) => <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />;
