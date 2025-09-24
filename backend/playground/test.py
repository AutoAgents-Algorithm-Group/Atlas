import asyncio
from pathlib import Path

from browser_use import Agent, ChatOpenAI
from browser_use.browser.events import ScreenshotEvent


async def my_step_hook(agent: Agent):
	# inside a hook you can access all the state and methods under the Agent object:
	#   agent.settings, agent.state, agent.task
	#   agent.tools, agent.llm, agent.browser_session
	#   agent.pause(), agent.resume(), agent.add_new_task(...), etc.

	# You also have direct access to the browser state
	state = await agent.browser_session.get_browser_state_summary()

	current_url = state.url
	visit_log = agent.history.urls()
	previous_url = visit_log[-2] if len(visit_log) >= 2 else None
	print(f'Agent was last on URL: {previous_url} and is now on {current_url}')
	cdp_session = await agent.browser_session.get_or_create_cdp_session()

	# Example: Get page HTML content
	doc = await cdp_session.cdp_client.send.DOM.getDocument(session_id=cdp_session.session_id)
	html_result = await cdp_session.cdp_client.send.DOM.getOuterHTML(
		params={'nodeId': doc['root']['nodeId']}, session_id=cdp_session.session_id
	)
	page_html = html_result['outerHTML']

	# Example: Take a screenshot using the event system
	screenshot_event = agent.browser_session.event_bus.dispatch(ScreenshotEvent(full_page=False))
	await screenshot_event
	result = await screenshot_event.event_result(raise_if_any=True, raise_if_none=True)

	# Example: pause agent execution and resume it based on some custom code
	if '/finished' in current_url:
		agent.pause()
		Path('result.txt').write_text(page_html)
		input('Saved "finished" page content to result.txt, press [Enter] to resume...')
		agent.resume()


async def main():
	agent = Agent(
		task='Search for the latest news about AI',
		llm=ChatOpenAI(
            model='gemini-2.5-pro',
            base_url="https://apihk.unifyllm.top/v1/messages",
            api_key="sk-kGlFBKwr3YQieh9dtWAF0hgkaLV7UcmJA1xJ9qZXOOQfvura"
            )
	)

	await agent.run(
		on_step_start=my_step_hook,
		# on_step_end=...
		max_steps=10,
	)


if __name__ == '__main__':
	asyncio.run(main())