#!/usr/bin/env bun
/**
 * TactileGenerate.ts - Generate tactile graphics using AI
 *
 * Wraps PAI's Art skill Generate.ts with tactile-specific prompt engineering.
 * Automatically appends the tactile suffix to ensure PIAF-ready output.
 *
 * Usage:
 *   bun run src/tools/TactileGenerate.ts --prompt "Floor plan of..." [OPTIONS]
 *
 * Examples:
 *   bun run TactileGenerate.ts --prompt "Floor plan of a two-bedroom apartment"
 *   bun run TactileGenerate.ts --prompt "Simplify this drawing" --reference source.jpg
 *   bun run TactileGenerate.ts --prompt "Barcelona Pavilion plan" --model gpt-image-1
 */

import { $ } from "bun";
import { existsSync } from "fs";
import { resolve, join } from "path";
import { homedir } from "os";

// The mandatory tactile suffix - appended to every prompt
const TACTILE_SUFFIX = `

Technical requirements for tactile output:
- Pure black lines on pure white background
- Minimum 2.5mm spacing between all distinct elements
- Bold solid lines, no fine details smaller than 1.5mm
- No gray tones, gradients, or shading
- No text or labels (Braille added separately)
- Consistent line weights throughout
- High contrast suitable for PIAF swell paper printing
- Simplified geometry - reduce curves to essential arcs
- Clear boundaries between distinct areas`;

interface GenerateOptions {
  prompt: string;
  model?: "flux-1.1-pro" | "nano-banana-pro" | "gpt-image-1" | "nano-banana" | "flux";
  reference?: string;
  output?: string;
  size?: "1K" | "2K" | "4K";
  aspectRatio?: string;
  layer?: "structure" | "circulation" | "program";
  skipSuffix?: boolean; // For advanced users who want custom suffix
}

function parseArgs(args: string[]): GenerateOptions {
  const options: GenerateOptions = {
    prompt: "",
    model: "flux-1.1-pro", // Default to Flux (most reliable)
    size: "1:1",
    aspectRatio: "1:1", // Square for floor plans
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case "--prompt":
      case "-p":
        options.prompt = args[++i];
        break;
      case "--model":
      case "-m":
        options.model = args[++i] as GenerateOptions["model"];
        break;
      case "--reference":
      case "-r":
        options.reference = args[++i];
        break;
      case "--output":
      case "-o":
        options.output = args[++i];
        break;
      case "--size":
      case "-s":
        options.size = args[++i] as GenerateOptions["size"];
        break;
      case "--aspect-ratio":
      case "-a":
        options.aspectRatio = args[++i];
        break;
      case "--layer":
      case "-l":
        options.layer = args[++i] as GenerateOptions["layer"];
        break;
      case "--skip-suffix":
        options.skipSuffix = true;
        break;
      case "-h":
      case "--help":
        printHelp();
        process.exit(0);
    }
  }

  return options;
}

function printHelp(): void {
  console.log(`
TactileGenerate - Generate tactile graphics using AI

Wraps PAI's Art skill with tactile-specific prompt engineering.
Automatically ensures PIAF-ready output specifications.

Usage:
  bun run TactileGenerate.ts --prompt "PROMPT" [OPTIONS]

Options:
  -p, --prompt TEXT         The generation prompt (required)
  -m, --model NAME          Model: nano-banana-pro (default), gpt-image-1, flux-1.1-pro
  -r, --reference PATH      Reference image for style/layout
  -o, --output PATH         Output file path (default: ~/Downloads/tactile-output.png)
  -s, --size SIZE           Size: 1K, 2K (default), 4K
  -a, --aspect-ratio RATIO  Aspect ratio (default: 17:22 for letter paper)
  -l, --layer TYPE          Stratification layer: structure, circulation, program
      --skip-suffix         Don't append tactile suffix (advanced)
  -h, --help                Show this help

Examples:
  # Generate from description
  bun run TactileGenerate.ts --prompt "Floor plan of two-bedroom apartment"

  # Simplify existing image
  bun run TactileGenerate.ts --prompt "Simplify this floor plan" --reference complex.jpg

  # Generate specific layer
  bun run TactileGenerate.ts --prompt "Show only structure" --layer structure

  # Use alternative model
  bun run TactileGenerate.ts --prompt "Barcelona Pavilion" --model gpt-image-1

Supported Models:
  nano-banana-pro   Google Gemini (recommended, supports reference images)
  gpt-image-1       OpenAI (alternative interpretation)
  flux-1.1-pro      Replicate (maximum detail control)
  nano-banana       Replicate (faster iteration)

The tactile suffix is automatically appended to ensure:
  - Pure black/white output
  - Bold lines (>1.5mm)
  - Adequate spacing (>2.5mm)
  - No gradients or text
`);
}

function buildPrompt(options: GenerateOptions): string {
  let prompt = options.prompt;

  // Add layer-specific prefix if specified
  if (options.layer) {
    const layerPrefixes: Record<string, string> = {
      structure: "Structural plan showing only load-bearing elements. ",
      circulation: "Circulation diagram showing only doors, stairs, and paths. ",
      program: "Program diagram showing only room boundaries for labeling. ",
    };
    prompt = layerPrefixes[options.layer] + prompt;
  }

  // Append tactile suffix unless skipped
  if (!options.skipSuffix) {
    prompt += TACTILE_SUFFIX;
  }

  return prompt;
}

async function generate(options: GenerateOptions): Promise<void> {
  // Validate prompt
  if (!options.prompt) {
    console.error("Error: --prompt is required");
    process.exit(1);
  }

  // Validate reference image if provided
  if (options.reference) {
    const refPath = resolve(options.reference);
    if (!existsSync(refPath)) {
      console.error(`Error: Reference image not found: ${refPath}`);
      process.exit(1);
    }
    options.reference = refPath;
  }

  // Set default output path
  if (!options.output) {
    const layerSuffix = options.layer ? `-${options.layer}` : "";
    options.output = join(homedir(), "Downloads", `tactile-output${layerSuffix}.png`);
  }

  // Build the full prompt with tactile suffix
  const fullPrompt = buildPrompt(options);

  // Path to PAI's Generate.ts
  const generateScript = join(homedir(), ".claude", "skills", "Art", "Tools", "Generate.ts");

  if (!existsSync(generateScript)) {
    console.error(`Error: PAI Art skill not found at ${generateScript}`);
    console.error("Make sure PAI is installed with the Art skill.");
    process.exit(1);
  }

  // Build command arguments
  const cmdArgs: string[] = [
    "bun", "run", generateScript,
    "--model", options.model!,
    "--prompt", fullPrompt,
    "--size", options.size!,
    "--aspect-ratio", options.aspectRatio!,
    "--output", options.output,
  ];

  if (options.reference) {
    cmdArgs.push("--reference", options.reference);
  }

  console.log("Generating tactile graphic...");
  console.log(`Model: ${options.model}`);
  console.log(`Output: ${options.output}`);
  if (options.layer) {
    console.log(`Layer: ${options.layer}`);
  }
  console.log("");

  try {
    // Execute PAI's Generate.ts
    const result = await $`${cmdArgs}`.text();
    console.log(result);

    // Verify output exists
    if (existsSync(options.output)) {
      console.log(`\nSuccess! Tactile graphic saved to: ${options.output}`);
      console.log("\nNext steps:");
      console.log("1. Review the image for PIAF compatibility");
      console.log("2. If needed, run through tactile-core for Braille labels:");
      console.log(`   tact convert ${options.output} --detect-text --braille-grade 2`);
    }
  } catch (error: any) {
    console.error(`Generation failed: ${error.message || error}`);

    // Provide troubleshooting tips
    if (error.message?.includes("API")) {
      console.log("\nTip: Check that API keys are configured in ~/.claude/.env");
    }
    if (error.message?.includes("quota")) {
      console.log("\nTip: Try a different model with --model flag");
    }

    process.exit(1);
  }
}

// Batch stratification helper
async function stratify(options: GenerateOptions): Promise<void> {
  const layers: Array<"structure" | "circulation" | "program"> = ["structure", "circulation", "program"];

  console.log("Generating stratified tactile output (3 layers)...\n");

  for (const layer of layers) {
    const layerOptions = {
      ...options,
      layer,
      output: options.output?.replace(".png", `-${layer}.png`) ||
        join(homedir(), "Downloads", `tactile-${layer}.png`),
    };

    console.log(`\n=== Generating ${layer} layer ===`);
    await generate(layerOptions);
  }

  console.log("\n=== Stratification complete ===");
  console.log("Generated 3 layers:");
  console.log("1. Structure - bearing walls, columns");
  console.log("2. Circulation - doors, stairs, paths");
  console.log("3. Program - room boundaries for Braille labels");
}

// Main execution
const args = process.argv.slice(2);

if (args.length === 0) {
  printHelp();
  process.exit(1);
}

// Check for stratify command
if (args.includes("--stratify")) {
  const options = parseArgs(args.filter(a => a !== "--stratify"));
  await stratify(options);
} else {
  const options = parseArgs(args);
  await generate(options);
}
