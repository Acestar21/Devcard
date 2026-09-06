import { NextRequest, NextResponse } from 'next/server';

const SESSION_COOKIE_NAME = 'devcard_session';

export async function GET(request: NextRequest) {
    const response = NextResponse.redirect(new URL('/', request.url));
    response.cookies.delete(SESSION_COOKIE_NAME);
    return response;
}