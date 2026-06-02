module.exports = async ({ github, context }) => {
    const report = process.env.REPORT;
    const commentBody = `## JSON Validation Failed\n\n${report}`;

    const { data: comments } = await github.rest.issues.listComments({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
    });

    const isDuplicate = comments.some(
        (c) => c.body.includes('## JSON Validation Failed') && c.body.includes(report)
    );

    if (isDuplicate) {
        console.log('Duplicate comment found, skipping...');
        return;
    }

    await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        body: commentBody,
    });
};
