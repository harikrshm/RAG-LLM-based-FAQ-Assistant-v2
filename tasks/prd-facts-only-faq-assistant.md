# Product Requirements Document: Facts-Only FAQ Assistant

## Introduction/Overview

The Facts-Only FAQ Assistant is a RAG (Retrieval-Augmented Generation) based chatbot widget that will be embedded into Groww's existing pages to answer factual questions about mutual fund schemes. The chatbot uses verified sources from official AMC (Asset Management Company), SEBI (Securities and Exchange Board of India), and AMFI (Association of Mutual Funds in India) websites to provide accurate, citation-backed responses.

**Problem Statement:** Users frequently have factual questions about mutual fund schemes (e.g., expense ratios, exit loads, minimum SIP amounts, lock-in periods, riskometer ratings, benchmarks, and how to download statements). Currently, these queries may require navigating multiple pages, contacting support, or searching through various sources, leading to increased support workload and potential user frustration.

**Solution:** An embedded chat widget that provides instant, accurate answers to factual questions using only verified official sources, with mandatory source citations for every response. The chatbot strictly avoids providing any investment advice and focuses solely on factual information.

**Goal:** Create a trustworthy, efficient FAQ assistant that reduces support workload, improves user trust through verified citations, and helps users quickly find specific scheme details without navigating multiple pages.

## Goals

1. **Reduce Support Workload:** Decrease the number of support tickets related to factual questions about mutual fund schemes by providing instant, accurate answers through the chatbot.

2. **Improve User Trust:** Build user confidence by providing citation-backed responses from verified official sources (AMC, SEBI, AMFI websites).

3. **Enhance User Experience:** Enable users to quickly find specific scheme details and any other factual information available in official sources without navigating multiple pages or contacting support.

4. **Ensure Accuracy:** Provide only factual information verified from official public pages, with every answer including at least one source link.

5. **Maintain Compliance:** Strictly avoid providing any investment advice, ensuring all responses are factual and informational only.

## User Stories

1. **As a Groww user**, I want to ask "What is the expense ratio of XYZ mutual fund scheme?" so that I can quickly get the factual information with a source link, without having to search through multiple pages.

2. **As a Groww user**, I want to know the exit load structure for a specific mutual fund scheme so that I can understand the charges before making investment decisions, with confidence that the information comes from official sources.

3. **As a Groww user**, I want to find out the minimum SIP amount for a scheme so that I can plan my investments accordingly, with the answer backed by an official source.

4. **As a Groww user**, I want to know if a scheme has a lock-in period (e.g., ELSS schemes) so that I can understand the liquidity implications, with information verified from official sources.

5. **As a Groww user**, I want to check the riskometer rating and benchmark of a mutual fund scheme so that I can assess the risk profile and performance comparison, with citations to official sources.

6. **As a Groww user**, I want to know how to download statements for my mutual fund investments so that I can access my account information, with guidance linked to official sources.

7. **As a Groww user**, when I ask a question that cannot be answered from available sources, I want to receive a helpful response directing me first to Groww's website pages (if available) or to official AMC/SEBI/AMFI websites so that I know where to find the information.

8. **As a Groww support team member**, I want users to get instant answers to common factual questions so that my workload is reduced and I can focus on more complex queries.

## Functional Requirements

### Core Functionality

1. The system must provide an embedded chat widget interface that can be integrated into existing Groww pages.

2. The system must accept user questions in natural language about mutual fund schemes from 5 AMCs (user will provide relevant source links during data collection).

3. The system must use RAG (Retrieval-Augmented Generation) architecture to retrieve relevant information from a knowledge base containing verified content from AMC, SEBI, and AMFI official public pages.

4. The system must use an LLM (Gemini or any open-source LLM) to generate concise, factual responses based on retrieved information.

5. The system must answer factual questions about all relevant data points found in the AMC source links, including but not limited to:
   - Expense ratio
   - Exit load
   - Minimum SIP amount
   - Lock-in period (e.g., ELSS schemes)
   - Riskometer rating
   - Benchmark
   - How to download statements
   - Any other factual information available in the official AMC, SEBI, or AMFI source pages

6. The system must include at least one source link in every answer. When information is available on Groww's website, the system should prioritize linking to the Groww page. Otherwise, the system should link back to the official AMC, SEBI, or AMFI webpage from which the information was retrieved.

7. The system must display source links in two formats:
   - Inline hyperlinks within the answer text where relevant
   - A separate "Sources" section at the end of each response listing all source URLs

8. The system must strictly avoid providing any investment advice, recommendations, or suggestions about which schemes to invest in.

9. The system must check if the requested information is available on Groww's website and direct users to the specific Groww page containing that information. If the information is not available on Groww's website, the system must then direct users to official AMC/SEBI/AMFI websites.

10. The system must provide concise, citation-backed responses that are easy to read and understand.

### Data and Source Requirements

11. The system must prioritize information from Groww's website when available. For information not available on Groww, the system must only use information from official public pages of AMC, SEBI, and AMFI websites.

12. The system must maintain a knowledge base containing verified content from 5 AMC mutual fund schemes (user will provide relevant source links during data collection phase).

13. The system must track and store source URLs for each piece of information in the knowledge base to enable citation generation.

14. The system must ensure that all source links are valid and accessible at the time of response generation.

### User Interface Requirements

15. The chat widget must be visually consistent with Groww's existing design system and brand guidelines. To ensure consistency, the following approach is recommended:
   - Extract Groww's design tokens (colors, typography, spacing, border radius, shadows) from their existing design system or component library
   - Use Groww's existing UI component library (if available) for buttons, inputs, and other interface elements
   - Create a shared style guide document or CSS variables file that maps Groww's design tokens to the widget's styling
   - Implement the widget using the same CSS framework or design system that Groww uses (e.g., Tailwind CSS with Groww's theme, Material-UI with custom theme, or Groww's proprietary component library)
   - Conduct visual regression testing against Groww's design system to ensure consistency
   - Maintain a design token mapping document that gets updated whenever Groww's design system evolves

16. The chat widget must be built for Groww's website platform and must be responsive to work across different desktop screen sizes.

17. The chat widget must display user questions and bot responses in a clear, readable format.

18. The chat widget must clearly distinguish between user messages and bot responses visually.

19. The chat widget must make source links clearly visible and clickable, opening in a new tab/window when clicked.

20. The chat widget must include a "Sources" section at the end of each response that lists all source URLs used.

### Error Handling and Edge Cases

21. The system must handle cases where no relevant information is found by first checking if the information exists on Groww's website and directing users to the specific Groww page. If not available on Groww, the system must then return a generic response directing users to official AMC/SEBI/AMFI websites.

22. The system must handle malformed or unclear user questions by asking for clarification or providing a helpful response.

23. The system must handle cases where source links become invalid or inaccessible gracefully (e.g., by indicating the source may no longer be available).

24. The system must handle high traffic and concurrent user requests without significant performance degradation.

## Non-Goals (Out of Scope)

1. **Investment Advice:** The chatbot will NOT provide any investment advice, recommendations, or suggestions about which schemes to invest in or when to invest.

2. **Performance Predictions:** The chatbot will NOT predict future performance, returns, or market trends.

3. **Personalized Recommendations:** The chatbot will NOT provide personalized investment recommendations based on user profile, risk appetite, or financial goals.

4. **Scheme Comparisons:** The chatbot will NOT compare different schemes or provide comparative analysis beyond factual data points.

5. **Portfolio Analysis:** The chatbot will NOT analyze user portfolios or provide portfolio-related advice.

6. **Transaction Support:** The chatbot will NOT help users execute transactions, place orders, or manage their investments.

7. **Account-Specific Information:** The chatbot will NOT access or display user-specific account information, holdings, or transaction history.

8. **Real-Time Data:** The chatbot will NOT provide real-time NAV (Net Asset Value) or live market data.

9. **Expansion Beyond Initial Scope:** The chatbot will initially focus on 5 AMC mutual funds only. Expansion to additional AMCs or financial products is out of scope for this initial version.

10. **Multi-language Support:** The chatbot will initially support English only. Multi-language support is out of scope for this version.

## Design Considerations

1. **Widget Placement:** The chat widget should be positioned in a non-intrusive location on Groww pages (e.g., bottom-right corner as a floating button that expands into a chat interface).

2. **Visual Design:** The widget should match Groww's existing design language, including colors, typography, and spacing.

3. **Chat Interface:** The interface should include:
   - A chat input field for user questions
   - A message history area displaying conversation
   - Clear visual distinction between user and bot messages
   - Loading indicators when the bot is processing a question
   - Source links styled as clickable buttons or underlined text

4. **Sources Section:** Each bot response should end with a clearly labeled "Sources" section that lists all source URLs in a readable format (e.g., bullet list with clickable links).

5. **Accessibility:** The widget should be accessible, including keyboard navigation support and screen reader compatibility.

6. **Responsive Design:** The widget should be responsive and optimized for different desktop screen sizes with appropriate sizing and interactions.

## Technical Considerations

1. **RAG Architecture:** The system should implement a RAG pipeline that includes:
   - Document ingestion and processing from official AMC/SEBI/AMFI websites
   - Vector embeddings generation for semantic search
   - Vector database for storing and retrieving relevant chunks
   - LLM integration (Gemini or open-source LLM) for response generation

2. **LLM Selection:** The system should support both Gemini and open-source LLM options, with the ability to switch between them based on requirements.

3. **Knowledge Base:** The knowledge base should be built from verified content scraped/crawled from official AMC, SEBI, and AMFI public pages. Source URLs must be preserved and linked to each content chunk. Additionally, the system should maintain a mapping of information available on Groww's website to enable directing users to relevant Groww pages when appropriate.

4. **Data Collection:** User will provide relevant source links for 5 AMC mutual funds during the data collection phase. The system should be designed to easily ingest and process these sources.

5. **Source Tracking:** The system must maintain a mapping between content chunks and their source URLs to enable accurate citation generation. The system should also maintain a mapping of factual information to corresponding Groww website pages (if available) to enable directing users to Groww pages first before external sources.

6. **Integration:** The chatbot widget should be integrated into Groww's existing infrastructure, potentially as a microservice or API that can be called from frontend pages.

7. **Performance:** The system should be optimized for low latency responses (target: < 3 seconds for typical queries).

8. **Scalability:** The architecture should support horizontal scaling to handle increased load.

9. **Monitoring:** The system should include logging and monitoring capabilities to track usage, response quality, and error rates.

10. **Data Updates:** Consideration should be given to how the knowledge base will be updated when source information changes (e.g., periodic re-crawling or manual updates).

## Success Metrics

1. **Support Ticket Reduction:** Measure the reduction in support tickets related to factual questions about mutual fund schemes. Target: 30% reduction within 3 months of launch.

2. **User Engagement:** Track the number of questions asked through the chatbot and user satisfaction ratings. Target: 10,000+ questions answered in the first month.

3. **Response Accuracy:** Monitor the accuracy of responses through user feedback and manual review. Target: 95%+ accuracy rate.

4. **Source Citation Rate:** Ensure 100% of responses include at least one source link.

5. **User Trust:** Measure user trust through surveys and feedback. Target: 80%+ users find the chatbot helpful and trustworthy.

6. **Response Time:** Track average response time for queries. Target: < 3 seconds for 90% of queries.

7. **Coverage:** Measure the percentage of user questions that can be answered from the knowledge base. Target: 70%+ answerable questions.

8. **Error Rate:** Monitor system errors and failures. Target: < 1% error rate.

## Open Questions

1. **Data Collection Timeline:** What is the timeline for collecting and processing source links for the 5 AMC mutual funds?

2. **Update Frequency:** How frequently should the knowledge base be updated to reflect changes in source information (e.g., monthly, quarterly)?

3. **LLM Preference:** Is there a preference between Gemini and open-source LLMs, or should the system support both with the ability to switch?

4. **Widget Placement:** Which specific Groww pages should the widget be embedded on initially? (e.g., scheme detail pages, help pages, homepage)

5. **User Feedback Mechanism:** Should the widget include a feedback mechanism (e.g., thumbs up/down) to collect user satisfaction data?

6. **Analytics Integration:** What analytics tools should be integrated to track usage and performance metrics?

7. **Content Moderation:** Should there be any content moderation or filtering for inappropriate user questions?

8. **Rate Limiting:** What rate limiting should be implemented to prevent abuse (e.g., questions per user per hour)?

9. **Fallback Response Details:** What specific wording should be used in the generic fallback response directing users to official websites?

10. **Testing Strategy:** What is the testing strategy for ensuring response accuracy and compliance with the no-advice policy?

