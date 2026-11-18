"""Command-line interface for pycodegraph."""

import click


@click.group()
@click.version_option()
def main() -> None:
    """pycodegraph - Static Python code analysis with LLM-generated summaries and diagram rendering."""
    pass


@main.command()
@click.option("--src", required=True, type=click.Path(exists=True), help="Source directory to analyze")
@click.option("--out", required=True, type=click.Path(), help="Output directory for JSON files")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def analyze(src: str, out: str, verbose: bool) -> None:
    """Analyze Python code and generate structure.json and calls.json."""
    click.echo(f"Analyzing {src}...")
    if verbose:
        click.echo("Verbose mode enabled")
    # TODO: Implement analyzer
    click.echo(f"Analysis complete. Output written to {out}")


@main.command()
@click.option("--input", "input_dir", required=True, type=click.Path(exists=True),
              help="Input directory containing JSON files")
@click.option("--provider", type=click.Choice(["openai", "anthropic", "gemini", "ollama"]),
              help="LLM provider")
@click.option("--model", help="Model name")
@click.option("--lang", default="cs", help="Summary language (default: cs)")
@click.option("--dry-run", is_flag=True, help="Show what would be processed without making API calls")
@click.option("--no-cache", is_flag=True, help="Disable cache")
@click.option("--refresh", is_flag=True, help="Refresh all cached entries")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def annotate(input_dir: str, provider: str | None, model: str | None, lang: str,
             dry_run: bool, no_cache: bool, refresh: bool, verbose: bool) -> None:
    """Generate LLM summaries and create annotations.json."""
    click.echo(f"Annotating code from {input_dir}...")
    if verbose:
        click.echo(f"Provider: {provider}, Model: {model}, Language: {lang}")
    if dry_run:
        click.echo("DRY RUN - no API calls will be made")
    # TODO: Implement annotator
    click.echo("Annotation complete")


@main.command()
@click.option("--input", "input_dir", required=True, type=click.Path(exists=True),
              help="Input directory containing JSON files")
@click.option("--format", type=click.Choice(["mermaid", "plantuml"]), default="mermaid",
              help="Output format (default: mermaid)")
@click.option("--diagram", type=click.Choice(["class", "sequence", "all"]), default="all",
              help="Diagram type to generate (default: all)")
@click.option("--entry", help="Entry point for sequence diagram (fully qualified name)")
@click.option("--depth", type=int, default=3, help="Maximum depth for sequence diagram (default: 3)")
@click.option("--output", type=click.Path(), help="Output file (default: stdout)")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def render(input_dir: str, format: str, diagram: str, entry: str | None,
           depth: int, output: str | None, verbose: bool) -> None:
    """Render Mermaid or PlantUML diagrams from JSON files."""
    click.echo(f"Rendering {diagram} diagram(s) from {input_dir}...")
    if verbose:
        click.echo(f"Format: {format}, Entry: {entry}, Depth: {depth}")
    # TODO: Implement renderer
    if output:
        click.echo(f"Diagram written to {output}")
    else:
        click.echo("# Diagram would be output here")


if __name__ == "__main__":
    main()
