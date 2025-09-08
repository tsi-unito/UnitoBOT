# UnitoBOT

A Telegram bot built with TypeScript and Grammy framework.

## Development Setup

### Prerequisites
- Node.js 18.x or higher
- npm or yarn
- PostgreSQL database

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the root directory with:
   ```
   TELEGRAM_API_KEY=<API KEY FROM BotFather>
   DATABASE_URL=postgresql://unito_bot:password@localhost:5432/unito_bot
   ```

### Available Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm run start` - Start the bot in production mode
- `npm run dev-server` - Start development server with hot reload
- `npm run test` - Run tests in watch mode
- `npm run test:ci` - Run tests once (for CI)
- `npm run lint` - Run ESLint code quality checks
- `npm run lint:fix` - Fix ESLint issues automatically
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check if code is properly formatted
- `npm run type-check` - Run TypeScript type checking without building
- `npm run ci` - Run full CI pipeline (type-check, lint, format-check, build, test)

## TypeScript Migration CI/CD

This project includes a comprehensive CI/CD pipeline optimized for TypeScript development:

### Automated Checks on Every Commit/PR:

1. **TypeScript Type Checking** - Validates all TypeScript types
2. **ESLint Code Quality** - Enforces coding standards and catches potential bugs
3. **Prettier Code Formatting** - Ensures consistent code style
4. **Build Validation** - Verifies the project compiles successfully
5. **Test Execution** - Runs the test suite
6. **Security Audit** - Checks for known vulnerabilities in dependencies
7. **Multi-Node Version Testing** - Tests compatibility across Node.js 18.x, 20.x, and 22.x

### Additional Quality Checks:

- **Bundle Size Analysis** - Tracks build output size
- **TypeScript Strict Mode Compliance** - Ensures strict TypeScript settings
- **Dependency Analysis** - Checks for unused dependencies
- **Docker Build Testing** - Validates containerization

### GitHub Actions Workflows:

- **`.github/workflows/ci.yml`** - Main CI/CD pipeline
- **`.github/workflows/typescript-quality.yml`** - Additional TypeScript-specific quality checks

### Configuration Files:

- **`tsconfig.json`** - TypeScript compiler configuration with strict settings
- **`eslint.config.js`** - ESLint configuration for TypeScript
- **`.prettierrc.json`** - Prettier code formatting rules
- **`vitest` configuration** - Modern testing framework setup

## Development Workflow

1. **Before committing**: Run `npm run ci` to ensure all checks pass
2. **Code formatting**: Use `npm run format` to auto-format your code
3. **Linting**: Use `npm run lint:fix` to automatically fix linting issues
4. **Testing**: Add tests for new features and run `npm test` during development

## Project Structure

```
src/
├── entities/           # Database entities (MikroORM)
├── commands/          # Bot command handlers
├── bot.ts            # Main bot entry point
└── mikro-orm.config.ts # Database configuration
```

## Technologies Used

- **TypeScript** - Type-safe JavaScript
- **Grammy** - Modern Telegram Bot framework
- **MikroORM** - TypeScript ORM for PostgreSQL
- **Vitest** - Fast unit testing framework
- **ESLint** - Code quality and consistency
- **Prettier** - Code formatting
- **Docker** - Containerization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the coding standards
4. Run `npm run ci` to ensure all checks pass
5. Submit a pull request

The CI/CD pipeline will automatically validate your changes across multiple Node.js versions and run all quality checks.