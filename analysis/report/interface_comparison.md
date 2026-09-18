# Homework 4 Interface Comparison

## Design Retained From The Reference Interface

I retained the reference interface's split between a human-readable trace view
and collapsible tool evidence. The detailed trace view still groups a tool call
with the immediately following tool result, keeps structured arguments/results
in monospace, and collapses long tool results by default. This matters because
tool outputs are often the evidence for a failure, but they should not dominate
the first pass through the conversation.

## Design Changed After Inspecting Cartwheel Traces

I changed the interface to show conversation context above the active trace.
Several Langfuse records are separate trace IDs for different turns in the same
scenario. For example, `919343cf848d7d3f4273b6df43bfd11a` and
`67817528c52390788eb68c3d377ca66f` are two turns from the same shopper
conversation. Reviewing either trace alone makes the follow-up harder to
interpret, so the interface now groups traces by `conversation_id` and displays
the user and assistant messages in chronological order. The active trace still
controls where annotations and labels attach.

I also added `user_id` to the trace header because authorization failures
depend on who is asking. The raw Langfuse export stored this value under
`metadata.attributes.cartwheel.user_id`, but the review header did not show it.
The updated normalizer preserves both the user id and a conversation id.

After trying the grouped conversation view, I removed tool calls and tool
results from that overview. Showing full JSON there made the top of the page
long and duplicated the detailed trace below. The overview now shows only user
and assistant messages, with role-tinted boxes and the trace id beside each
message.

Finally, I added a collapsed Ground Truth panel. It shows the current user,
merchant store, referenced orders, and recent scoped orders from
`data/cartwheel.db`. This helps distinguish an agent search failure from a true
absence in the database. The panel is evidence for human review; it does not
create labels automatically.

## Remaining Limitation

The interface still stores annotations and final labels against individual
trace IDs, even when the reviewer reads the whole grouped conversation for
context. This matches Langfuse score storage, but a later workflow may need an
explicit session-level summary if a failure spans multiple turns.
